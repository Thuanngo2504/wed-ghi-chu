import streamlit as st
import os
import re
import datetime


# Tạo thư mục lưu trữ ghi chú
if not os.path.exists("notes"):
    os.makedirs("notes")

# Hàm đọc ghi chú từ file
def read_notes():
    notes = []
    for file in os.listdir("notes"):
        if file.endswith(".txt"):
            with open(f"notes/{file}", "r", encoding="utf-8") as f:
                content = f.read()
                # Kiểm tra tag, pinned và nhắc nhở
                tags, pinned, reminder = [], False, None
                if "||tags||" in content:
                    parts = content.split("||tags||")
                    note_content = parts[0]
                    tags_pinned = parts[1].strip().split("||pinned||")
                    tags = tags_pinned[0].split(",") if tags_pinned[0] else []
                    pinned = tags_pinned[1].strip() == "True" if len(tags_pinned) > 1 else False
                    if "||reminder||" in content:
                        reminder = content.split("||reminder||")[-1].strip()
                        reminder = datetime.datetime.fromisoformat(reminder)
                else:
                    note_content = content
                
                notes.append({"title": file[:-4], "content": note_content, "tags": tags, "pinned": pinned, "reminder": reminder})
    return notes

# Hàm lưu ghi chú vào file
def save_note(title, content, tags=None, pinned=False, reminder=None):
    tags = tags or []
    with open(f"notes/{title}.txt", "w", encoding="utf-8") as f:
        f.write(content + f"||tags||{','.join(tags)}||pinned||{pinned}")
        if reminder:
            f.write(f"||reminder||{reminder}")

# Hàm xóa ghi chú
def delete_note(title):
    os.remove(f"notes/{title}.txt")

# Hàm sắp xếp ghi chú theo pinned và thời gian
def sort_notes(notes):
    return sorted(notes, key=lambda x: (not x["pinned"], x["title"]))

# Hàm kiểm tra nhắc nhở
def check_reminders():
    notes = read_notes()
    reminders = []
    for note in notes:
        if note["reminder"] and note["reminder"] > datetime.datetime.now():
            reminders.append((note["title"], note["reminder"]))
    return reminders
# Đọc và nhúng CSS từ file
def load_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# Giao diện Streamlit
st.set_page_config(page_title="Ứng dụng Ghi Chú", page_icon="📚", layout="wide")

# Cập nhật phần CSS để thêm ảnh nền
def add_background_image(image_path):
    background_css = f"""
    <style>
        .stApp {{
            background-image: url({image_path});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            height: 100vh;  /* Chiều cao của toàn bộ trang */
        }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

# Thêm ảnh nền từ file trong thư mục images
image_path = "images/hinh7.jpg"
add_background_image(image_path)


menu = st.sidebar.selectbox("📚 Chọn Chức năng", ["Tạo Ghi Chú", "Danh Sách Ghi Chú", "Tìm Kiếm", "Xóa Ghi Chú", "Chỉnh Sửa Ghi Chú", "Đặt Lịch Nhắc Nhở"])

st.title("Ứng dụng Ghi Chú")
st.subheader("Hãy để lại Ghi Chú của mình tại đây!")

# Kiểm tra và hiển thị nhắc nhở
reminders = check_reminders()
if reminders:
    st.sidebar.markdown("### 🔔 Nhắc Nhở:")
    for note, time in reminders:
        st.sidebar.write(f"**{note}** - {time.strftime('%Y-%m-%d %H:%M')}")

if menu == "Tạo Ghi Chú":
    st.header("Tạo Ghi Chú Mới")
    note_title = st.text_input("Tiêu đề ghi chú")
    note_content = st.text_area("Nội dung ghi chú")
    note_tags = st.text_input("Gắn nhãn (tags, cách nhau bởi dấu phẩy)")
    pinned = st.checkbox("Ghim ghi chú")

    if st.button("Lưu Ghi Chú"):
        if note_title and note_content:
            note_title = re.sub(r'[\/:*?"<>|]', '', note_title)
            save_note(note_title, note_content, tags=note_tags.split(","), pinned=pinned)
            st.success(f"Ghi chú '{note_title}' đã được lưu!")
        else:
            st.error("Vui lòng nhập đầy đủ tiêu đề và nội dung.")

elif menu == "Danh Sách Ghi Chú":
    st.header("Danh Sách Ghi Chú")
    notes = sort_notes(read_notes())  # Lấy danh sách ghi chú đã sắp xếp
    if notes:
        for note in notes:
            with st.expander(f"{'📌 ' if note['pinned'] else ''}{note['title']}"):
                st.write(note["content"])
                st.write(f"**Tags:** {', '.join(note['tags'])}")
                st.write(f"**Thời gian sửa đổi:** {datetime.datetime.fromtimestamp(os.path.getmtime(f'notes/{note['title']}.txt'))}")
                if st.button(f"Ghim {'bỏ' if note['pinned'] else ''} ghi chú", key=note["title"]):
                    save_note(note["title"], note["content"], note["tags"], not note["pinned"])
                    st.experimental_rerun()
    else:
        st.info("Không có ghi chú nào. Hãy thêm ghi chú mới!")

elif menu == "Xóa Ghi Chú":
    st.header("Xóa Ghi Chú")
    notes = read_notes()
    if notes:
        note_to_delete = st.selectbox("Chọn ghi chú để xóa", [note["title"] for note in notes])
        if st.button("Xóa Ghi Chú"):
            delete_note(note_to_delete)
            st.warning(f"Ghi chú '{note_to_delete}' đã bị xóa!")
            st.experimental_rerun()
    else:
        st.info("Không có ghi chú nào để xóa.")

elif menu == "Tìm Kiếm":
    st.header("Tìm Kiếm Ghi Chú")
    search_query = st.text_input("Nhập từ khóa tìm kiếm")
    notes = read_notes()
    results = [note for note in notes if search_query.lower() in note["title"].lower() or search_query.lower() in note["content"].lower()]
    if results:
        st.subheader("Kết quả tìm kiếm:")
        for note in results:
            with st.expander(note["title"]):
                st.write(note["content"])
    else:
        st.info("Không tìm thấy ghi chú phù hợp.")

elif menu == "Chỉnh Sửa Ghi Chú":
    st.header("Chỉnh Sửa Ghi Chú")
    notes = read_notes()
    if notes:
        note_to_edit = st.selectbox("Chọn ghi chú để chỉnh sửa", [note["title"] for note in notes])
        selected_note = next(note for note in notes if note["title"] == note_to_edit)
        new_content = st.text_area("Nội dung ghi chú", value=selected_note["content"])
        new_tags = st.text_input("Gắn nhãn mới", value=", ".join(selected_note["tags"]))
        new_pinned = st.checkbox("Ghim ghi chú", value=selected_note["pinned"])
        if st.button("Cập Nhật"):
            save_note(selected_note["title"], new_content, tags=new_tags.split(","), pinned=new_pinned, reminder=selected_note["reminder"])
            st.success("Ghi chú đã được cập nhật!")
            st.experimental_rerun()
    else:
        st.info("Không có ghi chú nào để chỉnh sửa.")

elif menu == "Đặt Lịch Nhắc Nhở":
    st.header("🔔 Đặt Lịch Nhắc Nhở")
    
    # Danh sách các ghi chú
    notes = os.listdir("notes")
    if notes:
        selected_note = st.selectbox("Chọn ghi chú để đặt nhắc nhở:", notes)
        
        # Chọn ngày và giờ
        reminder_date = st.date_input("Chọn ngày nhắc nhở:", datetime.date.today())
        reminder_time = st.time_input("Chọn giờ nhắc nhở:", datetime.datetime.now().time())
        
        # Nút lưu nhắc nhở
        if st.button("📅 Lưu Nhắc Nhở"):
            reminder_datetime = datetime.datetime.combine(reminder_date, reminder_time)
            
            # Lưu thời gian nhắc nhở vào file
            note_path = os.path.join("notes", selected_note)
            with open(note_path, "a", encoding="utf-8") as file:
                file.write(f"\n||reminder||{reminder_datetime}")
            
            st.success(f"Nhắc nhở cho ghi chú '{selected_note}' đã được đặt vào lúc {reminder_datetime}.")
    else:
        st.warning("⚠️ Không có ghi chú nào để đặt nhắc nhở. Hãy thêm ghi chú trước!")

# Hiển thị danh sách nhắc nhở
reminders = check_reminders()
if reminders:
    st.subheader("📅 Danh Sách Nhắc Nhở")
    for note, time in reminders:
        if time > datetime.datetime.now():
            st.write(f"🔔 **{note}** - Nhắc nhở vào lúc: {time.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.warning(f"⏰ **{note}** - Nhắc nhở đã hết hạn: {time.strftime('%Y-%m-%d %H:%M')}")
else:
    st.info("❗ Chưa có nhắc nhở nào được đặt.")
