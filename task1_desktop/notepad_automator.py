import os
import time
import subprocess
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.keyboard import send_keys
import pywinauto


class NotepadAutomator:
    def __init__(self, file_path):
        """
        Khởi tạo Automator với đường dẫn file cần lưu.
        Sử dụng backend 'uia' (UI Automation) phù hợp với Windows 10/11.
        """
        self.file_path = os.path.abspath(file_path)
        self.app = None
        self.main_window = None

    def launch(self):
        """Bước 1: Mở Notepad và chờ cửa sổ sẵn sàng."""
        print("[1] Launching Notepad...")
        try:
            self.app = Application(backend="uia").start("notepad.exe")
            # Dùng regex để bắt đúng cửa sổ trên cả Win 10 và Win 11
            self.main_window = self.app.window(title_re=".*Notepad.*")

            # SMART WAIT: Chờ đến khi cửa sổ sẵn sàng (tránh dùng time.sleep)
            self.main_window.wait('visible ready', timeout=10)
            print("    Notepad launched successfully.")
        except Exception as e:
            print(f"Error launching Notepad: {e}")
            raise

    def _get_edit_control(self):
        """Tìm Edit control trong cửa sổ Notepad."""
        try:
            edit = self.main_window.child_window(control_type="Edit")
            edit.wait('visible ready', timeout=5)
            return edit
        except Exception:
            # Fallback: thử tìm Document control (Win 11 new Notepad)
            edit = self.main_window.child_window(control_type="Document")
            edit.wait('visible ready', timeout=5)
            return edit

    def type_text(self, text):
        """
        Bước 2/3: Nhập text vào Notepad.
        Sử dụng clipboard paste để hỗ trợ Unicode (en-dash, v.v.).
        """
        print(f"[2/3] Typing text: '{text}'...")
        try:
            edit = self._get_edit_control()
            edit.set_focus()

            # Dùng clipboard paste để hỗ trợ ký tự Unicode đặc biệt (–, —, v.v.)
            self._clipboard_paste(text)
        except Exception as e:
            print(f"Error typing text: {e}")
            raise

    def _clipboard_paste(self, text):
        """
        Paste text vào ứng dụng đang focus thông qua clipboard.
        Sử dụng PowerShell Set-Clipboard — cách an toàn và đáng tin cậy nhất cho Unicode.
        """
        # Dùng PowerShell Set-Clipboard (có sẵn trên Windows 10+) để set clipboard
        # Escape single quotes bằng cách nhân đôi
        escaped = text.replace("'", "''")
        subprocess.run(
            ['powershell', '-Command', f"Set-Clipboard -Value '{escaped}'"],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # Paste bằng Ctrl+V
        send_keys('^v')
        time.sleep(0.5)  # Chờ paste hoàn tất

    def save_file(self):
        """Bước 4: Lưu file bằng Save As dialog."""
        print(f"[4] Saving file to: {self.file_path}")
        try:
            # Bấm tổ hợp phím Ctrl + S để mở Save As (file mới chưa lưu)
            self.main_window.type_keys("^s")
            time.sleep(1)  # Chờ dialog xuất hiện

            # Classic Notepad (Win 10): Save As dialog là #32770 thuộc win32 backend
            # Cần tìm bằng Desktop-level vì uia backend không thấy dialog ở app level
            save_dialog = pywinauto.Desktop(backend="win32").window(
                title="Save As",
                class_name="#32770"
            )
            save_dialog.wait('visible ready', timeout=10)

            # Tìm ô File Name (ComboBox Edit bên trong Save As dialog)
            file_name_edit = save_dialog.child_window(
                class_name="Edit",
                found_index=0
            )
            file_name_edit.wait('visible ready', timeout=5)

            # Điền đường dẫn file
            file_name_edit.set_edit_text(self.file_path)
            time.sleep(0.3)  # Chờ UI cập nhật

            # Click nút Save (Button "&Save")
            save_button = save_dialog.child_window(title="&Save", class_name="Button")
            save_button.click()

            # SAFEGUARD: Xử lý trường hợp file đã tồn tại (Confirm Save As)
            try:
                confirm_dialog = pywinauto.Desktop(backend="win32").window(
                    title="Confirm Save As",
                    class_name="#32770"
                )
                if confirm_dialog.exists(timeout=2):
                    print("    File already exists. Overwriting...")
                    confirm_dialog.child_window(title="&Yes", class_name="Button").click()
            except Exception:
                pass  # Không có dialog xác nhận = file mới, bỏ qua

            # Đảm bảo Save As dialog đã đóng trước khi đi tiếp
            save_dialog.wait_not('visible', timeout=10)
            print("    File saved successfully.")

        except ElementNotFoundError as e:
            print(f"Error: Save dialog elements not found. {e}")
            raise
        except Exception as e:
            print(f"Unexpected error during save: {e}")
            raise

    def close(self):
        """Đóng Notepad."""
        print("[*] Closing Notepad...")
        if self.app:
            try:
                self.app.kill()
            except Exception:
                pass  # Notepad đã đóng rồi

    def verify_content(self, expected_text):
        """
        OPTIONAL BONUS: Xác minh nội dung file đã lưu.
        Đọc trực tiếp từ disk để kiểm chứng Data Integrity.
        """
        print(f"[Bonus] Verifying content in: {self.file_path}")
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Verification failed: File not found at {self.file_path}")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            actual_text = f.read()

        # Notepad có thể thêm BOM, strip để so sánh chính xác
        actual_clean = actual_text.strip()
        expected_clean = expected_text.strip()

        if actual_clean == expected_clean:
            print("    ✅ SUCCESS: File content matches expected text.")
        else:
            print(f"    ❌ FAILED:")
            print(f"       Expected: '{expected_clean}'")
            print(f"       Actual:   '{actual_clean}'")
            raise AssertionError("Content mismatch")


if __name__ == "__main__":
    # --- Test Execution ---
    FILE_NAME = "vcaptech_automation_test.txt"

    # --- PRE-CLEANUP (Đảm bảo môi trường sạch trước khi chạy test) ---
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
        print(f"[*] Pre-cleanup: Removed existing file '{FILE_NAME}'.")
            
    PART_1_TEXT = "Desktop automation test"
    PART_2_TEXT = " – completed"  # Lưu ý: en-dash (U+2013)
    EXPECTED_FINAL_TEXT = PART_1_TEXT + PART_2_TEXT

    automator = NotepadAutomator(FILE_NAME)

    try:
        automator.launch()
        automator.type_text(PART_1_TEXT)
        automator.type_text(PART_2_TEXT)
        automator.save_file()
        automator.close()

        # Chạy hàm Bonus: kiểm tra nội dung file
        automator.verify_content(EXPECTED_FINAL_TEXT)

    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
    finally:
        automator.close()
        # Cleanup file sau khi test xong
        if os.path.exists(automator.file_path):
            os.remove(automator.file_path)
            print("[*] Cleanup: Test file deleted.")
