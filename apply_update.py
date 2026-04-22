import sys
import os
import time
import shutil
import subprocess
import zipfile
import tarfile
import argparse
import json

def extract_archive(archive_path, extract_to):
    """
    Safely extracts a ZIP or TAR.GZ archive, preventing path traversal attacks (Zip-Slip).
    """
    # Ensure the destination directory is an absolute path
    dest_dir = os.path.abspath(extract_to)

    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                # Prevent absolute paths and path traversal (../)
                if os.path.isabs(member) or '..' in member:
                    continue
                
                # Double-check the final resolved path stays within the target directory
                target_path = os.path.abspath(os.path.join(dest_dir, member))
                if not target_path.startswith(dest_dir + os.sep):
                    continue
                    
                zip_ref.extract(member, dest_dir)

    elif archive_path.endswith('.tar.gz'):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            # Safe extraction for Python 3.12+ to avoid DeprecationWarning
            if hasattr(tarfile, 'data_filter'):
                tar_ref.extractall(dest_dir, filter='data')
            else:
                # Fallback manual validation for older Python versions
                safe_members = []
                for member in tar_ref.getmembers():
                    if member.issym() or member.islnk():
                        continue # Skip symbolic/hard links
                    if os.path.isabs(member.name) or '..' in member.name:
                        continue
                    
                    target_path = os.path.abspath(os.path.join(dest_dir, member.name))
                    if target_path.startswith(dest_dir + os.sep):
                        safe_members.append(member)
                
                tar_ref.extractall(dest_dir, members=safe_members)


def main():
    parser = argparse.ArgumentParser(description="IlmQuiz Background Updater")
    parser.add_argument("--archive", required=True, help="Path to the downloaded update archive")
    parser.add_argument("--target", required=True, help="Path to the application installation folder")
    parser.add_argument("--exe", required=True, help="Name of the main executable to restart")
    parser.add_argument("--userdata", required=False, default="", help="Path to the user_data directory for status flags")
    args = parser.parse_args()

    # ==========================================
    # 🛡️ الترقيع الأمني: حارس المدخلات (Input Sanitization)
    # ==========================================
    # 1. منع استغلال مسار الملف التنفيذي (Directory Traversal)
    if os.path.basename(args.exe) != args.exe:
        print("SECURITY ALERT: Invalid --exe argument. Path traversal detected.")
        sys.exit(1)
        
    # 2. التأكد من أن الملف التنفيذي المطلوب تشغيله هو فعلاً الخاص باللعبة
    # (هذا يمنع استخدام أداتك لتشغيل برامج أخرى خبيثة)
    if args.exe.lower() not in ["ilmquiz.exe", "ilmquiz"]:
        print("SECURITY ALERT: Unauthorized executable name.")
        sys.exit(1)
        
    # 3. التأكد من أن مجلد الهدف موجود فعلاً لمنع الإنشاء العشوائي
    target_dir = os.path.abspath(args.target)
    if not os.path.isdir(target_dir):
        print("SECURITY ALERT: Target directory does not exist.")
        sys.exit(1)
    # ==========================================

    # 1. Give the main application 2 seconds to completely terminate
    time.sleep(2)

    # 2. Create a temporary extraction folder next to the target directory
    temp_ext_dir = os.path.join(target_dir, "_update_temp")
    os.makedirs(temp_ext_dir, exist_ok=True)
    
    update_success = False
    error_message = ""

    try:
        # Extract the downloaded archive
        extract_archive(args.archive, temp_ext_dir)

        # Handle the case where the archive contains a single root folder
        extracted_items = os.listdir(temp_ext_dir)
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_ext_dir, extracted_items[0])):
            source_dir = os.path.join(temp_ext_dir, extracted_items[0])
        else:
            source_dir = temp_ext_dir

        # Wait until the main executable is totally released by the OS locks
        target_exe_path = os.path.join(target_dir, args.exe)
        retries = 10
        while retries > 0:
            try:
                if os.path.exists(target_exe_path):
                    with open(target_exe_path, 'a'): pass
                break
            except Exception:
                time.sleep(1)
                retries -= 1

        # ==========================================
        # 3. The Rename Trick (Self-Update Workaround)
        # ==========================================
        current_updater = sys.executable
        if os.path.exists(current_updater):
            backup_updater = current_updater + ".old"
            try:
                if os.path.exists(backup_updater):
                    os.remove(backup_updater)
                os.rename(current_updater, backup_updater)
            except Exception:
                pass

        # 4. Overwrite the old files with the newly extracted ones
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        update_success = True

    except Exception as e:
        error_message = str(e)
        # Log failure silently for debugging purposes
        with open(os.path.join(target_dir, "updater_crash.log"), "w", encoding="utf-8") as f:
            f.write(f"Update failed: {error_message}")
    finally:
        # 5. Cleanup temporary extraction folder and the downloaded archive
        shutil.rmtree(temp_ext_dir, ignore_errors=True)
        try:
            os.remove(args.archive)
        except Exception:
            pass

        # Write status flag for the main application to read on next startup
        status_dir = args.userdata if args.userdata else target_dir
        if os.path.exists(status_dir):
            flag_file = os.path.join(status_dir, "update_status.json")
            try:
                with open(flag_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "success": update_success,
                        "error": error_message
                    }, f)
            except:
                pass

    # 6. Restart the main application
    if os.path.exists(target_exe_path):
        if sys.platform == "win32":
            subprocess.Popen([target_exe_path], creationflags=subprocess.DETACHED_PROCESS)
        else:
            subprocess.Popen([target_exe_path], start_new_session=True)

if __name__ == "__main__":
    main()
