import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="PriceTracker Pro | Market Intelligence",
    page_icon="📈",
    layout="wide"
)

# --- 2. Custom CSS for Modern UI (Dark/Light Responsive) ---
st.markdown("""
    <style>
    /* Styling for Metric Cards */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    /* Gradient Button */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #007bff, #00d4ff);
        color: white;
        border: none;
        font-weight: bold;
        width: 100%;
        height: 3em;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0, 123, 255, 0.4);
    }
    /* Progress Bar Color */
    .stProgress > div > div > div > div {
        background-color: #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Scraping Engine ---
def get_product_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Smart Title Detection
        title_tag = soup.find("h1") or soup.find(class_="product-title")
        title = title_tag.get_text().strip() if title_tag else "Unknown Product"
        
        # 2. Smart Price Detection (Common Tunisian E-commerce Tags)
        price_selectors = [
            ".current-price", "#our_price_display", ".price", 
            ".product-price", ".price-new", "[itemprop='price']"
        ]
        
        price_val = None
        for selector in price_selectors:
            found = soup.select_one(selector)
            if found:
                price_val = found.get_text().strip()
                break
        
        if price_val:
            # Clean non-numeric characters but keep decimal point
            clean_price = "".join(filter(lambda x: x.isdigit() or x in ".,", price_val))
            clean_price = clean_price.replace(',', '.')
            # Handle cases with multiple dots (e.g. 1.200.00)
            if clean_price.count('.') > 1:
                parts = clean_price.split('.')
                clean_price = "".join(parts[:-1]) + "." + parts[-1]
            
            return title, float(clean_price)
        return title, None
    except Exception as e:
        return None, None

# --- 4. Sidebar Interface ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/263/263142.png", width=80)
    st.title("Control Panel")
    st.markdown("---")
    target_url = st.text_input("🔗 Product Link", placeholder="Paste Jumia/MyTek link...")
    target_budget = st.number_input("🎯 Your Budget (TND)", min_value=0.0, step=10.0)
    st.markdown("---")
    start_btn = st.button("🚀 Analyze Price")

# --- 5. Main Dashboard Display ---
st.title("🛒 PriceTracker Pro")
st.caption("Professional Real-time E-commerce Scraper & Analysis Tool")

if start_btn:
    if not target_url:
        st.error("⚠️ Please provide a product URL first.")
    else:
        with st.spinner("🔍 Accessing store data..."):
            title, price = get_product_data(target_url)
            
            if price:
                st.subheader(f"Product: {title}")
                
                # Metric Cards
                m1, m2, m3 = st.columns(3)
                diff = price - target_budget
                
                m1.metric("Store Price", f"{price:,.2f} TND")
                m2.metric("Your Budget", f"{target_budget:,.2f} TND")
                m3.metric("Difference", f"{abs(diff):,.2f} TND", 
                          delta=f"-{diff:,.2f}" if diff > 0 else f"+{abs(diff):,.2f}",
                          delta_color="inverse" if diff > 0 else "normal")
                
                # Progress to Purchase
                progress_val = min(1.0, target_budget / price) if price > 0 else 0
                st.write(f"**Budget Readiness:** {int(progress_val*100)}%")
                st.progress(progress_val)
                
                # Action Center
                st.divider()
                if price <= target_budget:
                    st.balloons()
                    st.success("🎉 **Bargain Found!** The price is within your budget. Time to buy!")
                else:
                    st.info(f"💡 **Strategy:** You need the price to drop by another **{diff:,.2f} TND** to meet your goal.")
            else:
                st.error("❌ Error: Could not extract price data. The site might be blocking automated requests or using a different structure.")
else:
    # Welcome Screen
    st.info("👈 Enter a product URL in the sidebar to start tracking prices live.")
    st.image("https://via.placeholder.com/1000x300.png?text=Market+Insights+Dashboard+Preview", use_column_width=True)

st.divider()
st.caption("Developed with Python & Streamlit for Portfolio Showcase.")