import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CẤU HÌNH TRANG
st.set_page_config(
    page_title="Viet Tech TL;DR",
    page_icon="📰",
    layout="wide", # Dùng layout rộng để chia cột cho đẹp
    initial_sidebar_state="collapsed"
)

# CSS Tùy chỉnh cho đẹp hơn (Bo tròn ảnh, chỉnh font)
st.markdown("""
<style>
    .stImage img { border-radius: 10px; }
    .news-title { font-size: 20px; font-weight: bold; margin-bottom: 5px; }
    .news-meta { font-size: 12px; color: #666; margin-bottom: 10px; }
    .news-summary { font-size: 15px; line-height: 1.5; }
    .tag-span { background-color: #f0f2f6; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📰 Viet Tech TL;DR")
st.caption("Cập nhật tin công nghệ nóng hổi - Tóm tắt nhanh bởi AI")
st.divider()

# 2. KẾT NỐI DATA
try:
    # Kết nối Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Đọc dữ liệu (Thay 'TinTucTech' bằng tên Tab sheet của bạn)
    # TTL="10m" nghĩa là cache 10 phút mới tải lại 1 lần để đỡ tốn quota
    df = conn.read(worksheet="TinTucTech", ttl="1m")
    
    # Chuyển đổi cột thời gian để sắp xếp
    if 'published_at' in df.columns:
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
        df = df.sort_values(by='published_at', ascending=False)
    
    # Lọc tin: Chỉ hiện tin đã Publish (nếu cột is_published = TRUE)
    # Lưu ý: Google Sheet trả về TRUE/FALSE có thể là chuỗi hoặc boolean
    if 'is_published' in df.columns:
         # Dòng này đảm bảo lọc đúng dù là string "TRUE" hay boolean True
         df = df[df['is_published'].astype(str).str.upper() == 'TRUE']

except Exception as e:
    st.error(f"⚠️ Chưa kết nối được dữ liệu hoặc Sheet rỗng. Lỗi: {e}")
    st.stop()

# 3. HIỂN THỊ TIN TỨC
if df.empty:
    st.info("📭 Chưa có bài viết nào được xuất bản.")
else:
    for index, row in df.iterrows():
        # Tạo layout 2 cột: Cột 1 (Ảnh) - Cột 2 (Nội dung)
        col1, col2 = st.columns([1, 3], gap="medium")
        
        # --- CỘT TRÁI: ẢNH ---
        with col1:
            img_url = row.get('thumbnail_url')
            if pd.notna(img_url) and str(img_url).startswith('http'):
                st.image(img_url, use_container_width=True)
            else:
                # Ảnh mặc định nếu không có thumbnail
                st.image("https://via.placeholder.com/300x200?text=No+Image", use_container_width=True)

        # --- CỘT PHẢI: NỘI DUNG ---
        with col2:
            # Tiêu đề (Link tới bài gốc)
            original_url = row.get('original_url', '#')
            title = row.get('title_vn', 'Không có tiêu đề')
            st.markdown(f"### [{title}]({original_url})")
            
            # Thông tin phụ (Meta)
            source = row.get('source_name', 'Unknown')
            date_str = row['published_at'].strftime("%H:%M %d/%m") if pd.notna(row['published_at']) else ""
            category = row.get('category', 'General')
            st.markdown(f"**{source}** • {date_str} • *{category}*")
            
            # Tóm tắt
            summary = row.get('summary_vn', '')
            st.write(summary)
            
            # Tags (Hiển thị dạng chip)
            tags_raw = row.get('tags', '')
            if pd.notna(tags_raw) and str(tags_raw).strip() != "":
                # Xử lý chuỗi tag sạch hơn
                tags_list = str(tags_raw).replace("[","").replace("]","").replace("'","").split(",")
                st.markdown(" ".join([f"`#{t.strip()}`" for t in tags_list]), unsafe_allow_html=True)
        
        st.divider() # Gạch ngang phân cách bài

# Nút Footer
st.markdown("---")
st.caption("Made with ❤️ by Streamlit & Gemini AI")
