#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exteraGram Desktop - Automated branding patcher.
Applies exteraGram names, identifiers, and assets to the cloned upstream C++ repository.
"""

import os
import sys
import re
import argparse
import shutil

def patch_file(file_path: str, replacements: list[tuple[str, str]]) -> int:
    if not os.path.isfile(file_path):
        return 0

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        changed_count = 0
        new_content = content
        for old, new in replacements:
            if old in new_content:
                new_content = new_content.replace(old, new)
                changed_count += 1

        if changed_count > 0:
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_content)
            print(f"[PATCHED] {file_path} ({changed_count} replacements)")
            return changed_count
    except Exception as e:
        print(f"[ERROR] Failed to patch {file_path}: {e}")

    return 0

def patch_file_regex(file_path: str, pattern: str, replacement: str) -> int:
    if not os.path.isfile(file_path):
        return 0

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_content)
            print(f"[REGEX PATCHED] {file_path} ({count} replacements)")
            return count
    except Exception as e:
        print(f"[ERROR] Failed regex patch {file_path}: {e}")

    return 0

def apply_branding(target_dir: str):
    print(f"=== Applying exteraGram branding to: {target_dir} ===")

    total_patches = 0

    # 1. Patch Telegram/build/version
    version_file = os.path.join(target_dir, "Telegram", "build", "version")
    if os.path.exists(version_file):
        replacements = [
            ('AppFile "Telegram"', 'AppFile "exteraGram"'),
            ('AppNameOld "Telegram Desktop"', 'AppNameOld "exteraGram Desktop"'),
            ('AppName "Telegram Desktop"', 'AppName "exteraGram Desktop"'),
            ('AppShortName "Telegram"', 'AppShortName "exteraGram"'),
            ('AppName "AyuGram Desktop"', 'AppName "exteraGram Desktop"'),
            ('AppFile "AyuGram"', 'AppFile "exteraGram"'),
            ('AppShortName "AyuGram"', 'AppShortName "exteraGram"'),
        ]
        total_patches += patch_file(version_file, replacements)

    # 2. Patch CMakeLists.txt (Project naming)
    cmake_file = os.path.join(target_dir, "Telegram", "CMakeLists.txt")
    if os.path.exists(cmake_file):
        replacements = [
            ('set(output_name "Telegram")', 'set(output_name "exteraGram")'),
            ('set(output_name "AyuGram")', 'set(output_name "exteraGram")'),
        ]
        total_patches += patch_file(cmake_file, replacements)

    # 3. Patch core/version.h
    core_version = os.path.join(target_dir, "Telegram", "SourceFiles", "core", "version.h")
    if os.path.exists(core_version):
        replacements = [
            ('qstr("Telegram Desktop")', 'qstr("exteraGram Desktop")'),
            ('qstr("AyuGram Desktop")', 'qstr("exteraGram Desktop")'),
        ]
        total_patches += patch_file(core_version, replacements)

    # 4. Patch window titles and branding in UI
    main_window = os.path.join(target_dir, "Telegram", "SourceFiles", "window", "window_main_menu.cpp")
    if os.path.exists(main_window):
        replacements = [
            ('AppName.utf16()', 'u"exteraGram Desktop"_q'),
        ]
        total_patches += patch_file(main_window, replacements)

    # 5. Copy custom icons if available
    resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "resources")
    custom_icon = os.path.join(resources_dir, "icon.ico")
    custom_png = os.path.join(resources_dir, "icon.png")

    target_art_dir = os.path.join(target_dir, "Telegram", "Resources", "art")
    if os.path.isdir(target_art_dir):
        if os.path.exists(custom_icon):
            shutil.copyfile(custom_icon, os.path.join(target_art_dir, "icon.ico"))
            print(f"[ICON] Replaced Windows icon.ico")
        if os.path.exists(custom_png):
            for png_name in ["icon_16.png", "icon_32.png", "icon_48.png", "icon_64.png", "icon_128.png", "icon_256.png", "icon_512.png"]:
                dest = os.path.join(target_art_dir, png_name)
                if os.path.exists(dest):
                    try:
                        shutil.copyfile(custom_png, dest)
                    except Exception:
                        pass
            print(f"[ICON] Updated art PNG icons")

    print(f"=== Branding patches applied: {total_patches} modified entries ===")
    return total_patches

def run_test():
    print("=== Running self-test of patch_branding.py ===")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        # Create dummy version file
        build_dir = os.path.join(tmp, "Telegram", "build")
        os.makedirs(build_dir, exist_ok=True)
        vfile = os.path.join(build_dir, "version")
        with open(vfile, "w", encoding="utf-8") as f:
            f.write('AppFile "Telegram"\nAppNameOld "Telegram Desktop"\nAppName "Telegram Desktop"\n')

        # Test patching
        applied = apply_branding(tmp)
        with open(vfile, "r", encoding="utf-8") as f:
            content = f.read()

        assert 'AppFile "exteraGram"' in content, "AppFile was not replaced"
        assert 'AppName "exteraGram Desktop"' in content, "AppName was not replaced"
        print("[SUCCESS] Self-test verified: patcher replaced target definitions accurately.")

def main():
    parser = argparse.ArgumentParser(description="exteraGram Desktop Branding Patcher")
    parser.add_argument("--target", help="Path to cloned tdesktop/AyuGram source directory", default=None)
    parser.add_argument("--test", action="store_true", help="Run internal validation self-test")

    args = parser.parse_args()

    if args.test:
        run_test()
        sys.exit(0)

    if not args.target:
        print("[ERROR] Please provide --target <path_to_source> or use --test")
        sys.exit(1)

    apply_branding(os.path.abspath(args.target))

if __name__ == "__main__":
    main()
