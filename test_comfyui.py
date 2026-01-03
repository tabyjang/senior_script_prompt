"""
ComfyUI Integration Test Script
Tests the connection and image generation with Z-Image Turbo workflow.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.comfyui_service import ComfyUIService, ZImageWorkflowBuilder, BatchProcessor


def test_connection():
    """Test ComfyUI server connection."""
    print("=" * 50)
    print("Testing ComfyUI Connection...")
    print("=" * 50)

    comfyui = ComfyUIService()

    if comfyui.is_connected():
        print("[OK] ComfyUI is connected!")

        stats = comfyui.get_system_stats()
        if stats:
            system = stats.get("system", {})
            print(f"  Version: {system.get('comfyui_version', 'unknown')}")

            devices = stats.get("devices", [])
            for dev in devices:
                vram_gb = dev.get("vram_total", 0) / (1024**3)
                print(f"  GPU: {dev.get('name', 'unknown')} ({vram_gb:.1f} GB)")

        queue = comfyui.get_queue_status()
        running = len(queue.get("queue_running", []))
        pending = len(queue.get("queue_pending", []))
        print(f"  Queue: {running} running, {pending} pending")

        return True
    else:
        print("[ERROR] Cannot connect to ComfyUI!")
        print("  Make sure ComfyUI is running at http://127.0.0.1:8188")
        return False


def test_workflow_builder():
    """Test workflow builder with template."""
    print("\n" + "=" * 50)
    print("Testing Workflow Builder...")
    print("=" * 50)

    template_path = os.path.join(
        os.path.dirname(__file__),
        "prompts", "workflows", "z_image_turbo.json"
    )

    if not os.path.exists(template_path):
        print(f"[ERROR] Template not found: {template_path}")
        return False

    builder = ZImageWorkflowBuilder(template_path)

    if builder.template:
        print("[OK] Template loaded successfully!")
        print(f"  Nodes: {list(builder.template.keys())}")

        # Test setting values
        builder.set_positive_prompt("test prompt")
        builder.set_seed(12345)
        builder.set_filename_prefix("test/output")

        workflow = builder.get_workflow()
        prompt_text = workflow.get("45", {}).get("inputs", {}).get("text", "")
        seed = workflow.get("50:50:49", {}).get("inputs", {}).get("seed", 0)
        prefix = workflow.get("9", {}).get("inputs", {}).get("filename_prefix", "")

        print(f"  Prompt: {prompt_text[:50]}...")
        print(f"  Seed: {seed}")
        print(f"  Prefix: {prefix}")

        return True
    else:
        print("[ERROR] Failed to load template!")
        return False


def test_single_generation():
    """Test generating a single image."""
    print("\n" + "=" * 50)
    print("Testing Single Image Generation...")
    print("=" * 50)

    comfyui = ComfyUIService()

    if not comfyui.is_connected():
        print("[SKIP] ComfyUI not connected")
        return False

    template_path = os.path.join(
        os.path.dirname(__file__),
        "prompts", "workflows", "z_image_turbo.json"
    )

    builder = ZImageWorkflowBuilder(template_path)

    # Test scene data
    test_scene = {
        "scene_id": "test_s01",
        "main_prompt": "masterpiece, best quality, photorealistic, 1woman, standing in modern office, professional attire, confident expression",
        "character_prompts": {
            "Test Character": "45 year old Korean woman, neat hairstyle, business suit"
        },
        "output_folder": "test_output",
        "filename_prefix": "test_scene_01"
    }

    print("Building workflow...")
    workflow = builder.build_from_scene(test_scene)

    print("Queuing prompt...")
    prompt_id = comfyui.queue_prompt(workflow)

    if prompt_id:
        print(f"[OK] Prompt queued: {prompt_id}")

        print("Waiting for completion...")
        result = comfyui.wait_for_completion(prompt_id, timeout=120)

        if result:
            print("[OK] Generation completed!")

            outputs = result.get("outputs", {})
            for node_id, output in outputs.items():
                if "images" in output:
                    for img in output["images"]:
                        print(f"  Generated: {img.get('filename', 'unknown')}")

            return True
        else:
            print("[ERROR] Generation failed or timed out!")
            return False
    else:
        print("[ERROR] Failed to queue prompt!")
        return False


def test_scene_json():
    """Test processing a scene JSON file."""
    print("\n" + "=" * 50)
    print("Testing Scene JSON Processing...")
    print("=" * 50)

    # Find a scene JSON file
    scene_dir = os.path.join(
        os.path.dirname(__file__),
        "prompts", "1년동거5억조건", "scenes"
    )

    scene_file = None
    for root, dirs, files in os.walk(scene_dir):
        for f in files:
            if f.endswith(".json"):
                scene_file = os.path.join(root, f)
                break
        if scene_file:
            break

    if not scene_file:
        print("[SKIP] No scene JSON files found")
        return False

    print(f"Found scene file: {os.path.basename(scene_file)}")

    import json
    with open(scene_file, 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)

    scenes = chapter_data.get("scenes", [])
    print(f"  Scenes: {len(scenes)}")

    if scenes:
        first_scene = scenes[0]
        print(f"  First scene: {first_scene.get('scene_id', 'unknown')}")
        print(f"  Main prompt: {first_scene.get('main_prompt', '')[:60]}...")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  ComfyUI Integration Test Suite")
    print("=" * 60)

    results = {}

    # Test 1: Connection
    results["connection"] = test_connection()

    # Test 2: Workflow Builder
    results["workflow"] = test_workflow_builder()

    # Test 3: Scene JSON
    results["scene_json"] = test_scene_json()

    # Test 4: Single Generation (optional - takes time)
    print("\n" + "-" * 50)
    response = input("Run image generation test? (y/N): ").strip().lower()
    if response == 'y':
        results["generation"] = test_single_generation()
    else:
        results["generation"] = None
        print("[SKIP] Generation test skipped")

    # Summary
    print("\n" + "=" * 60)
    print("  Test Results Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        if passed is None:
            status = "SKIPPED"
        elif passed:
            status = "PASSED"
        else:
            status = "FAILED"
        print(f"  {test_name}: {status}")

    print("=" * 60)


if __name__ == "__main__":
    main()
