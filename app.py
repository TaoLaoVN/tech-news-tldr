import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Cấu hình trang
st.set_page_config(
    page_title="Viet Tech TL;DR",
    page_icon="📰",
    layout="centered" # Hoặc 'wide' nếu thích rộng
)

# 2. Tiêu đề
st.title("📰 Viet Tech TL;DR")
st.caption("Cập nhật tin công nghệ nóng hổi mỗi sáng - Tóm tắt bởi AI")
st.divider()

# 3. Kết nối Google Sheets (Cache lại để đỡ load nhiều tốn quota)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Thay 'TinTucTech' bằng tên Worksheet (Tab) trong file Excel của bạn
    df = conn.read(worksheet="TinTucTech", usecols=[0, 1, 2, 3, 4, 5, 6], ttl="10m")
    
    # Sắp xếp tin mới nhất lên đầu (Giả sử cột A là Thời gian)
    # df = df.sort_values(by="Thời gian", ascending=False)
    
except Exception as e:
    st.error(f"Lỗi kết nối Data: {e}")
    st.stop()

# 4. Hiển thị tin tức (Loop qua từng dòng)
# Cấu trúc cột Sheet lúc nãy: [0:Time, 1:Source, 2:Link, 3:Img, 4:TitleVN, 5:Summary, 6:Tags]
# Lưu ý: Pandas đọc header là dòng 1. Hãy đảm bảo file Sheet có dòng tiêu đề.

if df.empty:
    st.info("Chưa có tin tức nào.")
else:
    for index, row in df.iterrows():
        # Tạo Container cho đẹp
        with st.container():
            # Ảnh bìa
            if pd.notna(row['Ảnh']) and str(row['Ảnh']).startswith('http'):
                st.image(row['Ảnh'], use_container_width=True)
            
            # Tiêu đề & Nguồn
            st.subheader(row['Tiêu Đề'])
            st.caption(f"🕒 {row['Thời gian']} | 📡 {row['Nguồn']}")
            
            # Tóm tắt
            st.write(row['Tóm Tắt'])
            
            # Link gốc
            st.markdown(f"👉 [Đọc bài gốc tại đây]({row['Link Gốc']})")
            
            # Tag (Chip)
            if pd.notna(row['Tags']):
                tags = str(row['Tags']).replace("[","").replace("]","").replace("'","").split(",")
                st.write("🏷️ " + " ".join([f"`{t.strip()}`" for t in tags]))
                
        st.divider() # Kẻ gạch ngang phân cách

# Nút reload thủ công
if st.button('🔄 Cập nhật tin mới'):
    st.rerun()