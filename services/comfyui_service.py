"""
ComfyUI API Service
Handles communication with local ComfyUI server for image generation.
"""

import json
import urllib.request
import urllib.error
import uuid
import os
import shutil
import time
from typing import Optional, Dict, Any, Callable
from pathlib import Path


class ComfyUIService:
    """ComfyUI API communication service"""

    def __init__(self, host: str = "127.0.0.1", port: int = 8188):
        """
        Initialize ComfyUI service.

        Args:
            host: ComfyUI server host
            port: ComfyUI server port
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.client_id = str(uuid.uuid4())

    def is_connected(self) -> bool:
        """Check if ComfyUI server is running and accessible."""
        try:
            req = urllib.request.Request(f"{self.base_url}/system_stats")
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False

    def get_system_stats(self) -> Optional[Dict[str, Any]]:
        """Get ComfyUI system statistics."""
        try:
            req = urllib.request.Request(f"{self.base_url}/system_stats")
            with urllib.request.urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return None

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        try:
            req = urllib.request.Request(f"{self.base_url}/queue")
            with urllib.request.urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode())
        except Exception:
            return {"queue_running": [], "queue_pending": []}

    def queue_prompt(self, workflow: Dict[str, Any]) -> Optional[str]:
        """
        Queue a prompt/workflow for execution.

        Args:
            workflow: ComfyUI workflow in API format

        Returns:
            Prompt ID if successful, None otherwise
        """
        try:
            payload = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            data = json.dumps(payload).encode('utf-8')

            req = urllib.request.Request(
                f"{self.base_url}/prompt",
                data=data,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                return result.get("prompt_id")

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"HTTP Error {e.code}: {error_body}")
            return None
        except Exception as e:
            print(f"Error queuing prompt: {e}")
            return None

    def get_history(self, prompt_id: str = None) -> Dict[str, Any]:
        """Get execution history."""
        try:
            url = f"{self.base_url}/history"
            if prompt_id:
                url = f"{url}/{prompt_id}"

            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception:
            return {}

    def wait_for_completion(
        self,
        prompt_id: str,
        timeout: int = 300,
        poll_interval: float = 1.0,
        progress_callback: Callable[[int, int], None] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for a prompt to complete execution.

        Args:
            prompt_id: The prompt ID to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Time between status checks
            progress_callback: Optional callback (current, total)

        Returns:
            Execution result or None if timeout/error
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check history for completion
            history = self.get_history(prompt_id)

            if prompt_id in history:
                result = history[prompt_id]
                if "outputs" in result:
                    return result
                if "error" in result:
                    print(f"Execution error: {result.get('error')}")
                    return None

            # Check queue status
            queue = self.get_queue_status()
            running = queue.get("queue_running", [])
            pending = queue.get("queue_pending", [])

            # Find our prompt position
            total_queue = len(running) + len(pending)
            position = 0
            for i, item in enumerate(running + pending):
                if len(item) > 1 and item[1] == prompt_id:
                    position = i + 1
                    break

            if progress_callback and total_queue > 0:
                progress_callback(position, total_queue)

            time.sleep(poll_interval)

        print(f"Timeout waiting for prompt {prompt_id}")
        return None

    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> Optional[bytes]:
        """
        Download an image from ComfyUI.

        Args:
            filename: Image filename
            subfolder: Subfolder within output directory
            folder_type: 'output', 'input', or 'temp'

        Returns:
            Image bytes or None
        """
        try:
            params = f"filename={filename}&subfolder={subfolder}&type={folder_type}"
            url = f"{self.base_url}/view?{params}"

            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read()
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    def save_output_images(
        self,
        result: Dict[str, Any],
        output_dir: str,
        prefix: str = ""
    ) -> list:
        """
        Save generated images from execution result.

        Args:
            result: Execution result from wait_for_completion
            output_dir: Directory to save images
            prefix: Optional filename prefix

        Returns:
            List of saved file paths
        """
        saved_files = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        outputs = result.get("outputs", {})
        for node_id, node_output in outputs.items():
            if "images" not in node_output:
                continue

            for img_info in node_output["images"]:
                filename = img_info.get("filename", "")
                subfolder = img_info.get("subfolder", "")
                folder_type = img_info.get("type", "output")

                image_data = self.get_image(filename, subfolder, folder_type)
                if image_data:
                    # Generate output filename
                    if prefix:
                        ext = Path(filename).suffix
                        new_filename = f"{prefix}_{filename}"
                    else:
                        new_filename = filename

                    save_path = output_path / new_filename
                    with open(save_path, "wb") as f:
                        f.write(image_data)
                    saved_files.append(str(save_path))

        return saved_files


class WorkflowBuilder:
    """Build ComfyUI workflows from templates and scene prompts."""

    def __init__(self, template_path: str = None):
        """
        Initialize workflow builder.

        Args:
            template_path: Path to base workflow JSON template
        """
        self.template = None
        if template_path and os.path.exists(template_path):
            self.load_template(template_path)

    def load_template(self, path: str) -> bool:
        """Load a workflow template from file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.template = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading template: {e}")
            return False

    def set_template(self, workflow: Dict[str, Any]):
        """Set workflow template directly."""
        self.template = workflow

    def find_node_by_type(self, class_type: str) -> Optional[str]:
        """Find a node ID by its class type."""
        if not self.template:
            return None

        for node_id, node_data in self.template.items():
            if node_data.get("class_type") == class_type:
                return node_id
        return None

    def find_nodes_by_type(self, class_type: str) -> list:
        """Find all node IDs matching a class type."""
        nodes = []
        if not self.template:
            return nodes

        for node_id, node_data in self.template.items():
            if node_data.get("class_type") == class_type:
                nodes.append(node_id)
        return nodes

    def set_positive_prompt(self, prompt: str, node_id: str = None) -> bool:
        """
        Set the positive prompt in the workflow.

        Args:
            prompt: The positive prompt text
            node_id: Specific node ID, or auto-detect if None
        """
        if not self.template:
            return False

        if node_id is None:
            # Find CLIPTextEncode node (positive is usually first)
            nodes = self.find_nodes_by_type("CLIPTextEncode")
            if nodes:
                node_id = nodes[0]

        if node_id and node_id in self.template:
            self.template[node_id]["inputs"]["text"] = prompt
            return True
        return False

    def set_negative_prompt(self, prompt: str, node_id: str = None) -> bool:
        """Set the negative prompt in the workflow."""
        if not self.template:
            return False

        if node_id is None:
            # Find second CLIPTextEncode node (negative)
            nodes = self.find_nodes_by_type("CLIPTextEncode")
            if len(nodes) > 1:
                node_id = nodes[1]

        if node_id and node_id in self.template:
            self.template[node_id]["inputs"]["text"] = prompt
            return True
        return False

    def set_seed(self, seed: int = None, node_id: str = None) -> bool:
        """Set the seed for KSampler."""
        if not self.template:
            return False

        if seed is None:
            seed = int(time.time() * 1000) % (2**32)

        if node_id is None:
            node_id = self.find_node_by_type("KSampler")

        if node_id and node_id in self.template:
            self.template[node_id]["inputs"]["seed"] = seed
            return True
        return False

    def set_filename_prefix(self, prefix: str, node_id: str = None) -> bool:
        """Set output filename prefix in SaveImage node."""
        if not self.template:
            return False

        if node_id is None:
            node_id = self.find_node_by_type("SaveImage")

        if node_id and node_id in self.template:
            self.template[node_id]["inputs"]["filename_prefix"] = prefix
            return True
        return False

    def set_image_size(self, width: int, height: int, node_id: str = None) -> bool:
        """Set image size in EmptyLatentImage node."""
        if not self.template:
            return False

        if node_id is None:
            node_id = self.find_node_by_type("EmptyLatentImage")

        if node_id and node_id in self.template:
            self.template[node_id]["inputs"]["width"] = width
            self.template[node_id]["inputs"]["height"] = height
            return True
        return False

    def get_workflow(self) -> Dict[str, Any]:
        """Get the current workflow."""
        return self.template.copy() if self.template else {}

    def build_from_scene(self, scene: Dict[str, Any], base_negative: str = "") -> Dict[str, Any]:
        """
        Build a workflow from a scene prompt JSON.

        Args:
            scene: Scene data from scene prompt JSON
            base_negative: Base negative prompt to use

        Returns:
            Complete workflow for ComfyUI API
        """
        if not self.template:
            raise ValueError("No template loaded")

        # Get main prompt
        main_prompt = scene.get("main_prompt", "")

        # Get character prompts and combine
        character_prompts = scene.get("character_prompts", {})
        if character_prompts:
            char_prompt_parts = list(character_prompts.values())
            full_prompt = f"{main_prompt}, {', '.join(char_prompt_parts)}"
        else:
            full_prompt = main_prompt

        # Set prompts
        self.set_positive_prompt(full_prompt)
        if base_negative:
            self.set_negative_prompt(base_negative)

        # Set filename prefix if available
        prefix = scene.get("filename_prefix", "")
        if prefix:
            self.set_filename_prefix(prefix)

        # Randomize seed
        self.set_seed()

        return self.get_workflow()


class ZImageWorkflowBuilder(WorkflowBuilder):
    """Specialized builder for Z-Image Turbo workflow."""

    # Z-Image Turbo specific node IDs
    PROMPT_NODE = "45"          # CLIPTextEncode
    SAMPLER_NODE = "50:50:49"   # KSampler
    SAVE_NODE = "9"             # SaveImage
    LATENT_NODE = "41"          # EmptySD3LatentImage

    def set_positive_prompt(self, prompt: str, node_id: str = None) -> bool:
        """Set the positive prompt (Z-Image uses node 45)."""
        if not self.template:
            return False
        target_node = node_id or self.PROMPT_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["text"] = prompt
            return True
        return False

    def set_seed(self, seed: int = None, node_id: str = None) -> bool:
        """Set the seed for KSampler (Z-Image uses node 50:50:49)."""
        if not self.template:
            return False
        # 시드 고정값 사용 (None이면 기본 고정값)
        if seed is None:
            seed = 12345678  # 고정 시드값
        target_node = node_id or self.SAMPLER_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["seed"] = seed
            return True
        return False

    def set_filename_prefix(self, prefix: str, node_id: str = None) -> bool:
        """Set output filename prefix (Z-Image uses node 9)."""
        if not self.template:
            return False
        target_node = node_id or self.SAVE_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["filename_prefix"] = prefix
            return True
        return False

    def set_image_size(self, width: int, height: int, node_id: str = None) -> bool:
        """Set image size (Z-Image uses EmptySD3LatentImage node 41)."""
        if not self.template:
            return False
        target_node = node_id or self.LATENT_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["width"] = width
            self.template[target_node]["inputs"]["height"] = height
            return True
        return False

    def build_from_scene(self, scene: Dict[str, Any], base_negative: str = "", project_name: str = "") -> Dict[str, Any]:
        """Build workflow from scene data (Z-Image doesn't use negative prompt)."""
        if not self.template:
            raise ValueError("No template loaded")

        import copy
        workflow = copy.deepcopy(self.template)
        self.template = workflow

        # Get main prompt
        main_prompt = scene.get("main_prompt", "")

        # Get character prompts and combine
        character_prompts = scene.get("character_prompts", {})
        if character_prompts:
            char_prompt_parts = list(character_prompts.values())
            full_prompt = f"{main_prompt}, {', '.join(char_prompt_parts)}"
        else:
            full_prompt = main_prompt

        # Set prompt
        self.set_positive_prompt(full_prompt)

        # Set filename prefix - save to project/act folder
        output_folder = scene.get("output_folder", "output")
        from pathlib import Path
        path_parts = Path(output_folder).parts
        act_name = path_parts[1] if len(path_parts) > 1 else "output"
        prefix = scene.get("filename_prefix", "scene")

        if project_name:
            full_prefix = f"{project_name}/{act_name}/{prefix}"
        else:
            full_prefix = f"{act_name}/{prefix}"
        self.set_filename_prefix(full_prefix)

        # Randomize seed
        self.set_seed()

        return self.get_workflow()


class QwenWorkflowBuilder(WorkflowBuilder):
    """Specialized builder for Qwen Image workflow."""

    # Qwen specific node IDs
    PROMPT_NODE = "101"         # CLIPTextEncode (Positive)
    NEGATIVE_NODE = "87"        # CLIPTextEncode (Negative)
    SAMPLER_NODE = "97"         # KSampler
    SAVE_NODE = "60"            # SaveImage
    LATENT_NODE = "86"          # EmptySD3LatentImage

    def set_positive_prompt(self, prompt: str, node_id: str = None) -> bool:
        """Set the positive prompt (Qwen uses node 101)."""
        if not self.template:
            return False

        target_node = node_id or self.PROMPT_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["text"] = prompt
            return True
        return False

    def set_negative_prompt(self, prompt: str, node_id: str = None) -> bool:
        """Set the negative prompt (Qwen uses node 87)."""
        if not self.template:
            return False

        target_node = node_id or self.NEGATIVE_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["text"] = prompt
            return True
        return False

    def set_seed(self, seed: int = None, node_id: str = None) -> bool:
        """Set the seed for KSampler (Qwen uses node 97)."""
        if not self.template:
            return False
        # 시드 고정값 사용 (None이면 기본 고정값)
        if seed is None:
            seed = 12345678  # 고정 시드값
        target_node = node_id or self.SAMPLER_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["seed"] = seed
            return True
        return False

    def set_filename_prefix(self, prefix: str, node_id: str = None) -> bool:
        """Set output filename prefix (Qwen uses node 60)."""
        if not self.template:
            return False

        target_node = node_id or self.SAVE_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["filename_prefix"] = prefix
            return True
        return False

    def set_image_size(self, width: int, height: int, node_id: str = None) -> bool:
        """Set image size (Qwen uses EmptySD3LatentImage node 86)."""
        if not self.template:
            return False

        target_node = node_id or self.LATENT_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["width"] = width
            self.template[target_node]["inputs"]["height"] = height
            return True
        return False

    def build_from_scene(self, scene: Dict[str, Any], base_negative: str = "", project_name: str = "") -> Dict[str, Any]:
        """Build workflow from scene data."""
        if not self.template:
            raise ValueError("No template loaded")

        # Deep copy template to avoid modifying original
        import copy
        workflow = copy.deepcopy(self.template)
        self.template = workflow

        # Get main prompt
        main_prompt = scene.get("main_prompt", "")

        # Get character prompts and combine
        character_prompts = scene.get("character_prompts", {})
        if character_prompts:
            char_prompt_parts = list(character_prompts.values())
            full_prompt = f"{main_prompt}, {', '.join(char_prompt_parts)}"
        else:
            full_prompt = main_prompt

        # Set prompt
        self.set_positive_prompt(full_prompt)

        # Set negative prompt if provided
        if base_negative:
            self.set_negative_prompt(base_negative)

        # Set filename prefix - save to project/act folder
        # output_folder: "scenes/act1/ep01/s01_arrival" -> "act1"
        output_folder = scene.get("output_folder", "output")
        from pathlib import Path
        path_parts = Path(output_folder).parts  # ('scenes', 'act1', 'ep01', 's01_arrival')
        act_name = path_parts[1] if len(path_parts) > 1 else "output"  # 'act1'
        prefix = scene.get("filename_prefix", "scene")

        # Build path: project_name/act_name/filename
        if project_name:
            full_prefix = f"{project_name}/{act_name}/{prefix}"
        else:
            full_prefix = f"{act_name}/{prefix}"
        self.set_filename_prefix(full_prefix)

        # Randomize seed
        self.set_seed()

        return self.get_workflow()

    def set_positive_prompt(self, prompt: str, node_id: str = None) -> bool:
        """Set the positive prompt (Z-Image uses node 45)."""
        if not self.template:
            return False

        target_node = node_id or self.PROMPT_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["text"] = prompt
            return True
        return False

    def set_seed(self, seed: int = None, node_id: str = None) -> bool:
        """Set the seed for KSampler (Z-Image uses node 50:50:49)."""
        if not self.template:
            return False

        if seed is None:
            seed = int(time.time() * 1000) % (2**53)

        target_node = node_id or self.SAMPLER_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["seed"] = seed
            return True
        return False

    def set_filename_prefix(self, prefix: str, node_id: str = None) -> bool:
        """Set output filename prefix (Z-Image uses node 9)."""
        if not self.template:
            return False

        target_node = node_id or self.SAVE_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["filename_prefix"] = prefix
            return True
        return False

    def set_image_size(self, width: int, height: int, node_id: str = None) -> bool:
        """Set image size (Z-Image uses EmptySD3LatentImage node 41)."""
        if not self.template:
            return False

        target_node = node_id or self.LATENT_NODE
        if target_node in self.template:
            self.template[target_node]["inputs"]["width"] = width
            self.template[target_node]["inputs"]["height"] = height
            return True
        return False

    def build_from_scene(self, scene: Dict[str, Any], base_negative: str = "", project_name: str = "") -> Dict[str, Any]:
        """Build workflow from scene data (Z-Image doesn't use negative prompt)."""
        if not self.template:
            raise ValueError("No template loaded")

        # Deep copy template to avoid modifying original
        import copy
        workflow = copy.deepcopy(self.template)
        self.template = workflow

        # Get main prompt
        main_prompt = scene.get("main_prompt", "")

        # Get character prompts and combine
        character_prompts = scene.get("character_prompts", {})
        if character_prompts:
            char_prompt_parts = list(character_prompts.values())
            full_prompt = f"{main_prompt}, {', '.join(char_prompt_parts)}"
        else:
            full_prompt = main_prompt

        # Set prompt
        self.set_positive_prompt(full_prompt)

        # Set filename prefix - save to project/act folder
        # output_folder: "scenes/act1/ep01/s01_arrival" -> "act1"
        output_folder = scene.get("output_folder", "output")
        from pathlib import Path
        path_parts = Path(output_folder).parts  # ('scenes', 'act1', 'ep01', 's01_arrival')
        act_name = path_parts[1] if len(path_parts) > 1 else "output"  # 'act1'
        prefix = scene.get("filename_prefix", "scene")

        # Build path: project_name/act_name/filename
        if project_name:
            full_prefix = f"{project_name}/{act_name}/{prefix}"
        else:
            full_prefix = f"{act_name}/{prefix}"
        self.set_filename_prefix(full_prefix)

        # Randomize seed
        self.set_seed()

        return self.get_workflow()


class BatchProcessor:
    """Process multiple scene prompts in batch."""

    def __init__(
        self,
        comfyui: ComfyUIService,
        workflow_builder: WorkflowBuilder,
        base_output_dir: str = "output"
    ):
        """
        Initialize batch processor.

        Args:
            comfyui: ComfyUIService instance
            workflow_builder: WorkflowBuilder with loaded template
            base_output_dir: Base directory for output images
        """
        self.comfyui = comfyui
        self.builder = workflow_builder
        self.base_output_dir = base_output_dir
        self.default_negative = "worst quality, low quality, blurry, deformed"

    def process_scene(
        self,
        scene: Dict[str, Any],
        progress_callback: Callable[[str, int, int], None] = None
    ) -> list:
        """
        Process a single scene and generate image.

        Args:
            scene: Scene data from JSON
            progress_callback: Optional callback (status, current, total)

        Returns:
            List of saved image paths
        """
        scene_id = scene.get("scene_id", "unknown")
        output_folder = scene.get("output_folder", "output")

        # Build workflow
        workflow = self.builder.build_from_scene(scene, self.default_negative)

        # Queue prompt
        if progress_callback:
            progress_callback(f"Queuing {scene_id}...", 0, 1)

        prompt_id = self.comfyui.queue_prompt(workflow)
        if not prompt_id:
            print(f"Failed to queue scene {scene_id}")
            return []

        # Wait for completion
        if progress_callback:
            progress_callback(f"Generating {scene_id}...", 0, 1)

        result = self.comfyui.wait_for_completion(prompt_id)
        if not result:
            print(f"Failed to generate scene {scene_id}")
            return []

        # Save images
        output_dir = os.path.join(self.base_output_dir, output_folder)
        prefix = scene.get("filename_prefix", scene_id)
        saved = self.comfyui.save_output_images(result, output_dir, prefix)

        if progress_callback:
            progress_callback(f"Completed {scene_id}", 1, 1)

        return saved

    def process_chapter(
        self,
        chapter_data: Dict[str, Any],
        progress_callback: Callable[[str, int, int], None] = None
    ) -> Dict[str, list]:
        """
        Process all scenes in a chapter.

        Args:
            chapter_data: Chapter JSON data with scenes array
            progress_callback: Optional callback (status, current, total)

        Returns:
            Dict mapping scene_id to list of saved paths
        """
        results = {}
        scenes = chapter_data.get("scenes", [])
        total = len(scenes)

        for i, scene in enumerate(scenes):
            scene_id = scene.get("scene_id", f"scene_{i}")

            if progress_callback:
                progress_callback(f"Processing {scene_id}", i, total)

            saved = self.process_scene(scene)
            results[scene_id] = saved

        return results

    def process_json_file(
        self,
        json_path: str,
        progress_callback: Callable[[str, int, int], None] = None
    ) -> Dict[str, list]:
        """
        Process all scenes from a JSON file.

        Args:
            json_path: Path to chapter JSON file
            progress_callback: Optional callback

        Returns:
            Dict mapping scene_id to list of saved paths
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            return self.process_chapter(chapter_data, progress_callback)
        except Exception as e:
            print(f"Error processing file {json_path}: {e}")
            return {}
