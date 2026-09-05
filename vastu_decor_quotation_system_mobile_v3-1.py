import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
from fpdf import FPDF

# --- SET PAGE CONFIG (MOBILE WEB VIEW OPTIMIZED) ---
st.set_page_config(
    page_title="Vastu Décor Mobile Studio",
    page_icon="🛋️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- MASTER CATALOG DATABASE ---
# Grouped by Category for beautiful mobile navigation
PRODUCT_CATALOG = {
    "🛋️ Sofa & Seating": [
        ("Sofa Making (Normal Standard)", 3900, "Per Rft"),
        ("Sofa Making (Premium Class)", 4800, "Per Rft"),
        ("Sofa Modification & Repairs", 1500, "Per Rft"),
        ("Standard Headrest Cushion", 1250, "Per Set"),
        ("Premium Backrest Seating", 1850, "Per Rft"),
        ("Indian Seating Mattress Set", 12500, "Per Set"),
        ("Sofa Loose Cover (Normal Fabric)", 350, "Per Seat"),
        ("Sofa Loose Cover (Premium Velvet)", 650, "Per Seat"),
        ("Puffy / Footrest Custom", 2400, "Per Nos")
    ],
    "🛏️ Beds & Mattress": [
        ("Bed In Ply & Laminate (6' x 7')", 69780, "Per Set"),
        ("Modern Cushioning Double Bed", 37400, "Per Set"),
        ("Dressing Table with Polish & Mirrors", 27840, "Per Set"),
        ("Jitu Premium 9\" Spring Mattress", 18500, "Per Nos"),
        ("Ortho Coir 6\" Century Premium", 14500, "Per Nos"),
        ("Memory Foam Luxury 6\" Mattress", 16800, "Per Nos"),
        ("Memory Foam Luxury 8\" Mattress", 21500, "Per Nos"),
        ("Custom Headboard Cushioning", 180, "Per Sqft")
    ],
    "🚪 Curtains & Blinds": [
        ("AP Premium Curtains (Sarom)", 1250, "Per Mtr"),
        ("Roman Style Curtains with Track", 1450, "Per Nos"),
        ("Curtain Lining & Track Fitting", 180, "Per Rft"),
        ("Roller Blinds (Regular)", 260, "Per Sqft"),
        ("Roller Blinds (Premium Customized)", 339, "Per Sqft"),
        ("Duplex Roller Blinds (Zebra)", 420, "Per Sqft"),
        ("Wooden Venetian Blinds", 550, "Per Sqft"),
        ("Monsoon Protection Blinds (Outdoor)", 290, "Per Sqft")
    ],
    "✨ False Ceiling": [
        ("Gypsum False Ceiling (JSW Frame)", 75, "Per Sqft"),
        ("PVC Sheet Ceiling Fixing", 57, "Per Sqft"),
        ("Premium Wooden Pattern Ceiling", 185, "Per Sqft"),
        ("Metal Grid False Ceiling (Commercial)", 110, "Per Sqft"),
        ("Ceiling LED Profile Track Light", 350, "Per Rft")
    ],
    "🖼️ Wallpaper & Paint": [
        ("Wallpaper Roll Pasting (Premium)", 4800, "Per Roll"),
        ("3D Customized Mural Wallpaper", 270, "Per Sqft"),
        ("Asian Paint Royale Luxury Coat", 45, "Per Sqft"),
        ("Asian Paint Tractor Emulsion Coat", 22, "Per Sqft"),
        ("Apex Outer Shield Weather Paint", 35, "Per Sqft"),
        ("P.U. Coat Polish Work (Wood Finish)", 240, "Per Sqft"),
        ("Melamyne Gold Polish Work (Wood Finish)", 120, "Per Sqft")
    ],
    "🧱 Flooring & Carpet": [
        ("Wooden Flooring Herringbone Pattern", 185, "Per Sqft"),
        ("Non-Oven Soft Carpet Tiles", 65, "Per Sqft"),
        ("Gym High-Density Rubber Carpet", 140, "Per Sqft"),
        ("Artificial Grass Flooring (30mm Premium)", 85, "Per Sqft"),
        ("Artificial Grass Flooring (40mm Super Premium)", 110, "Per Sqft"),
        ("Vinyl Flooring Sheet Fixing", 75, "Per Sqft")
    ],
    "🍽️ Kitchen & Wardrobe": [
        ("Kitchen Trolly Tendom System", 6075, "Per Rft"),
        ("Kitchen Shutters Acrylic Finish", 1450, "Per Sqft"),
        ("Wardrobe with Sliding Doors (Laminate)", 2100, "Per Sqft"),
        ("Wardrobe Veneer Finish with Polish", 2850, "Per Sqft")
    ]
}

# --- STANDARD SOFA MATERIAL COEFFICIENTS PER RFT (Based on Jitu Bhai 25.5 Rft model) ---
SOFA_COEFFICIENTS = [
    ("50 Density 4'' Foam For Seat", 4.5 / 25.5, "Sheets", 3200),
    ("50 Density 2'' Foam", 4.5 / 25.5, "Sheets", 1600),
    ("1'' Supersoft Foam For Seat", 4.5 / 25.5, "Sheets", 1150),
    ("40 Density 3'' Foam For Back", 4.5 / 25.5, "Sheets", 2680),
    ("12 MM Foam Layering", 10.0 / 25.5, "Sheets", 350),
    ("Fibre Recron", 13.0 / 25.5, "Mtr", 310),
    ("Zig Zag Clip / Spring Support", 5.0 / 25.5, "Bundles", 1080),
    ("Hook U Khila (Nails)", 180.0 / 25.5, "Nos", 4),
    ("2'' X 2'' Wooden Frame (Akashi)", 2.5 / 25.5, "Cu. Ft", 810),
    ("Kiltan (Underlying Fabric)", 13.0 / 25.5, "Mtr", 100),
    ("Spray Gun Solution (Pasting)", 1.0 / 25.5, "Lump Sum", 3400),
    ("Hydrolic Gun Pins", 1.0 / 25.5, "Lump Sum", 380),
    ("18 mm Waterproof Plywood", 4.0 / 25.5, "Sheets", 2720),
    ("12 mm Waterproof Plywood", 3.0 / 25.5, "Sheets", 2080),
    ("6 mm Flexi Plywood", 4.0 / 25.5, "Sheets", 1500),
    ("Decorative Legs For Sofa", 18.0 / 25.5, "Nos", 340),
    ("Branded Cloth For Seat & Back", 29.0 / 25.5, "Mtr", 938),
    ("Branded Rexine For Handle & Border", 15.5 / 25.5, "Mtr", 938),
    ("Labour For Cushion/Upholstery", 1.0, "Rft", 600),
    ("Labour For Carpentry Frame Work", 1.0, "Rft", 400)
]

# --- SESSION STATE INITIALIZATION ---
if "quote_items" not in st.session_state:
    st.session_state.quote_items = []

# --- CUSTOM CSS FOR REAL NATIVE PHONE APP LOOK ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Poppins', sans-serif;
        background-color: #F8FAFC;
    }
    
    /* Header & Navigation Styling */
    .app-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        padding: 20px 15px;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 25px;
        color: white;
    }
    
    .app-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 12px;
        opacity: 0.8;
        margin: 5px 0 0 0;
    }

    /* Cards/Modules on Phone */
    .mobile-card {
        background-color: white;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #E2E8F0;
    }
    
    .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Input Elements styling for mobile fingers */
    .stNumberInput input, .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border-radius: 10px !important;
        border: 1.5px solid #CBD5E1 !important;
        padding: 10px !important;
        background-color: #FAFAFA !important;
        font-size: 14px !important;
    }
    
    /* Big touch-friendly buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.25) !important;
        transition: all 0.2s ease;
        width: 100% !important;
        height: auto !important;
    }
    
    div.stButton > button:active {
        transform: scale(0.97);
        opacity: 0.95;
    }
    
    /* Secondary/Clear Buttons */
    .clear-btn button {
        background: #EF4444 !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25) !important;
    }
    
    /* Responsive live totals banner */
    .total-banner {
        background: #ECFDF5;
        border-left: 5px solid #10B981;
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1);
    }
    
    .total-title {
        font-size: 13px;
        color: #065F46;
        font-weight: 500;
        margin: 0;
    }
    
    .total-amount {
        font-size: 26px;
        color: #047857;
        font-weight: 700;
        margin: 2px 0 0 0;
    }
    
    /* Tabs custom layout */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #E2E8F0;
        padding: 6px;
        border-radius: 14px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px;
        background-color: transparent;
        border: none;
        color: #475569;
        font-weight: 500;
        font-size: 13px;
        flex-grow: 1;
        text-align: center;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #1E3A8A !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- PROFESSIONAL APP HEADER ---
st.markdown("""
<div class="app-header">
    <div class="app-title">VASTU DÉCOR</div>
    <div class="app-subtitle">🛋️ Professional Mobile Studio & Billing</div>
</div>
""", unsafe_allow_html=True)

# --- TAB NAVIGATION (Fits perfectly on phone screen) ---
tab_client, tab_sofa, tab_catalog, tab_review, tab_export = st.tabs([
    "👤 Client", 
    "🛋️ Sofa", 
    "📦 Catalog", 
    "📑 Review", 
    "📤 Share"
])

# --- TAB 1: CLIENT DETAILS ---
with tab_client:
    st.markdown("""
    <div class="mobile-card">
        <div class="card-title">📝 Client & Business Details</div>
    </div>
    """, unsafe_allow_html=True)
    
    client_name = st.text_input("Customer Name:", value="Chimasaheb Rasal Sir")
    client_address = st.text_input("Customer Address:", value="Sangli")
    quote_date = st.date_input("Quotation Date:", datetime.date.today())
    
    st.markdown("""
    <div style='background-color:#EFF6FF; border-left:4px solid #3B82F6; padding:10px; border-radius:8px; font-size:12px; color:#1E40AF; margin-top:15px;'>
        💡 <b>Business Address:</b><br>
        Vastu Décor, 100 Ft. Road, Near Ghatage Patil Honda Showroom, Royal Ganesh Apart, Shop B1, B4, Sangli | Contact: 7756059999
    </div>
    """, unsafe_allow_html=True)

# --- TAB 2: SOFA MATERIAL AUTO-CALCULATOR ---
with tab_sofa:
    st.markdown("""
    <div class="mobile-card">
        <div class="card-title">🛋️ Sofa Material Auto-Estimator</div>
        <p style="font-size: 12px; color: #64748B; margin-top: -8px;">
            Enter the exact sofa length in Running Feet. The system will automatically compute the exact quantities for all 20 premium materials.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    sofa_length = st.number_input("Sofa Length (Running Feet - Rft):", min_value=1.0, max_value=100.0, value=15.0, step=0.5)
    
    if st.button("➕ Auto-Calculate & Add All 20 Sofa Materials", key="sofa_add_btn"):
        # Remove existing Sofa items to avoid double counts on update
        st.session_state.quote_items = [item for item in st.session_state.quote_items if "Sofa:" not in item["particulars"]]
        
        # Proportional calculation
        for name, coeff, unit, rate in SOFA_COEFFICIENTS:
            qty = round(coeff * sofa_length, 2)
            total = round(qty * rate, 2)
            st.session_state.quote_items.append({
                "particulars": f"Sofa: {name} (for {sofa_length} Rft)",
                "qty": qty,
                "unit": unit,
                "rate": rate,
                "total": total
            })
        st.success(f"🎉 Successfully added all 20 detailed materials for {sofa_length} Rft sofa!")

# --- TAB 3: PRO-CATALOG & CUSTOM ITEMS ---
with tab_catalog:
    # Option 1: Standard Catalog Selection
    st.markdown("""
    <div class="mobile-card">
        <div class="card-title">📦 Master Catalog Item</div>
    </div>
    """, unsafe_allow_html=True)
    
    selected_category = st.selectbox("Choose Category:", list(PRODUCT_CATALOG.keys()))
    category_items = PRODUCT_CATALOG[selected_category]
    
    item_names = [item[0] for item in category_items]
    selected_item_name = st.selectbox("Choose Item Type:", item_names)
    
    # Retrieve details
    item_rate = 0
    item_unit = "Nos"
    for item in category_items:
        if item[0] == selected_item_name:
            item_rate = item[1]
            item_unit = item[2]
            break
            
    cat_qty = st.number_input("Quantity / Metric:", min_value=0.1, value=1.0, step=0.5, key="cat_qty")
    cat_rate = st.number_input("Rate (Rs.):", min_value=1, value=int(item_rate), key="cat_rate")
    
    st.markdown(f"<div style='font-size:12px; color:#475569; margin: -8px 0 10px 0;'>Unit of Measure: <b>{item_unit}</b></div>", unsafe_allow_html=True)
    
    if st.button("➕ Add Catalog Item", key="add_cat_btn"):
        tot = round(cat_qty * cat_rate, 2)
        st.session_state.quote_items.append({
            "particulars": selected_item_name,
            "qty": cat_qty,
            "unit": item_unit,
            "rate": cat_rate,
            "total": tot
        })
        st.success(f"Added: {selected_item_name}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Option 2: Custom Fresh Item Form
    st.markdown("""
    <div class="mobile-card">
        <div class="card-title">✏️ Add Custom New Item</div>
    </div>
    """, unsafe_allow_html=True)
    
    custom_name = st.text_input("Item Name / Description:", placeholder="e.g. Center Table with Marble Top")
    col1, col2 = st.columns(2)
    with col1:
        custom_qty = st.number_input("Custom Qty:", min_value=0.1, value=1.0, step=0.5, key="cust_qty")
        custom_unit = st.text_input("Custom Unit:", value="Nos", key="cust_unit")
    with col2:
        custom_rate = st.number_input("Custom Rate (Rs.):", min_value=0, value=1000, step=100, key="cust_rate")
        
    if st.button("➕ Add Custom Item", key="add_cust_btn"):
        if custom_name.strip() == "":
            st.error("Please enter a valid custom item name.")
        else:
            tot = round(custom_qty * custom_rate, 2)
            st.session_state.quote_items.append({
                "particulars": custom_name.strip(),
                "qty": custom_qty,
                "unit": custom_unit,
                "rate": custom_rate,
                "total": tot
            })
            st.success(f"Added custom item: {custom_name}")

# --- TAB 4: REVIEW & MANAGE ITEMS ---
with tab_review:
    st.markdown("""
    <div class="mobile-card">
        <div class="card-title">📑 Active Items List</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.quote_items:
        st.info("Your active quotation list is empty. Add some items first!")
    else:
        # Shaded review table for mobile
        df_items = pd.DataFrame(st.session_state.quote_items)
        df_display = df_items.copy()
        df_display["qty"] = df_display["qty"].map(lambda x: f"{x:.2f}")
        df_display["rate"] = df_display["rate"].map(lambda x: f"Rs. {x:,}")
        df_display["total"] = df_display["total"].map(lambda x: f"Rs. {x:,.2f}")
        
        st.dataframe(df_display, use_container_width=True)
        
        # Totals logic
        subtotal = sum(item["total"] for item in st.session_state.quote_items)
        
        # Live GST selection
        add_gst = st.checkbox("Include 18% GST (Required for Bank Trans)", value=False, key="review_gst")
        
        grand_total = subtotal
        gst_amt = 0.0
        if add_gst:
            gst_amt = subtotal * 0.18
            grand_total = subtotal + gst_amt
            
        st.markdown(f"""
        <div class="total-banner">
            <div class="total-title">LIVE GRAND TOTAL</div>
            <div class="total-amount">Rs. {grand_total:,.2f}</div>
            <div style="font-size:11px; color:#047857; margin-top:4px;">
                Subtotal: Rs. {subtotal:,.2f} {" | GST (18%): Rs. " + f"{gst_amt:,.2f}" if add_gst else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Delete item controller
        st.markdown("##### 🗑️ Manage Individual Items")
        item_options = [f"{idx+1}. {item['particulars']} (Rs. {item['total']:,})" for idx, item in enumerate(st.session_state.quote_items)]
        selected_del_item = st.selectbox("Select an item to remove:", item_options)
        
        if st.button("❌ Remove Selected Item", key="del_item_btn"):
            idx_to_del = int(selected_del_item.split(".")[0]) - 1
            if 0 <= idx_to_del < len(st.session_state.quote_items):
                removed = st.session_state.quote_items.pop(idx_to_del)
                st.success(f"Removed: {removed['particulars']}")
                st.rerun()
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Entire Quotation", key="clear_all_btn"):
            st.session_state.quote_items = []
            st.success("Entire quotation has been cleared!")
            st.rerun()

# --- TAB 5: PDF GENERATOR & WHATSAPP EXPORT ---
with tab_export:
    st.markdown("""
    <div class="mobile-card">
        <div class="card-title">📤 Share & Export Quotation</div>
        <p style="font-size:12px; color:#475569; margin-top:-8px;">
            Send this directly to client on WhatsApp or download a highly professional, formatted PDF invoice/quotation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.quote_items:
        st.info("No active items to share. Please build your quotation first!")
    else:
        # Live math
        subtotal = sum(item["total"] for item in st.session_state.quote_items)
        add_gst = st.session_state.get("review_gst", False)
        gst_amt = subtotal * 0.18 if add_gst else 0.0
        grand_total = subtotal + gst_amt

        # 1. WHATSAPP COPY BANNER
        st.markdown("##### 💬 Text Copy for WhatsApp")
        export_txt = "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        export_txt += "         *VASTU DÉCOR*\n"
        export_txt += "   _Interior Furnishing Studio_\n"
        export_txt += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        export_txt += f"*Client:* {client_name}\n"
        export_txt += f"*Address:* {client_address}\n"
        export_txt += f"*Date:* {quote_date.strftime('%d-%m-%Y')}\n"
        export_txt += "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for idx, item in enumerate(st.session_state.quote_items, 1):
            export_txt += f"*{idx}. {item['particulars']}*\n"
            export_txt += f"   Qty: {item['qty']} {item['unit']}\n"
            export_txt += f"   Rate: Rs. {item['rate']:,}\n"
            export_txt += f"   *Total: Rs. {item['total']:,.2f}*\n\n"
            
        export_txt += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        export_txt += f"*Subtotal:* Rs. {subtotal:,.2f}\n"
        if add_gst:
            export_txt += f"*GST (18%):* Rs. {gst_amt:,.2f}\n"
        export_txt += f"*GRAND TOTAL:* *Rs. {grand_total:,.2f}*\n"
        export_txt += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        export_txt += "*Notes:*\n"
        export_txt += "1. Prices are calculated based on actual measurements.\n"
        export_txt += "2. 18% GST is extra if paid via bank/online transaction.\n\n"
        export_txt += "Thank you for choosing Vastu Décor!\n"
        export_txt += "Contact: 7756059999\n"
        
        st.text_area("Double tap to select & copy this format directly to WhatsApp:", value=export_txt, height=220)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 2. PDF INVOICE GENERATION ENGINE (FPDF2)
        st.markdown("##### 📄 Export Professional PDF File")
        
        # PDF builder function
        def create_pdf_bytes():
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Company Banner/Header
            pdf.set_fill_color(31, 78, 120) # Deep Navy #1F4E78
            pdf.rect(0, 0, 210, 38, 'F')
            
            # Company Name in White
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 10, "VASTU DECOR", ln=True, align="C")
            
            # Company Details in White
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 5, "Royal Ganesh Apart, Shop B1, B4, Near Ghatage Patil Honda, 100 Ft Road, Sangli", ln=True, align="C")
            pdf.cell(0, 5, "Contact: +91 7756059999 | Email: contact@vastudecor.com", ln=True, align="C")
            pdf.ln(12)
            
            # Reset text color
            pdf.set_text_color(30, 41, 59)
            
            # Document Title & Client Info (Two column block)
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(100, 6, "QUOTATION ESTIMATE", ln=False)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, f"Date: {quote_date.strftime('%d-%m-%Y')}", ln=True, align="R")
            
            pdf.set_draw_color(226, 232, 240)
            pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
            pdf.ln(4)
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(100, 5, f"Client Name: {client_name}", ln=False)
            pdf.cell(0, 5, f"Location: {client_address}", ln=True, align="R")
            pdf.ln(6)
            
            # Table Headers
            pdf.set_fill_color(241, 245, 249)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_draw_color(226, 232, 240)
            
            pdf.cell(12, 8, "Sr No", border=1, ln=False, fill=True, align="C")
            pdf.cell(95, 8, "Material / Particular Description", border=1, ln=False, fill=True, align="L")
            pdf.cell(20, 8, "Qty", border=1, ln=False, fill=True, align="R")
            pdf.cell(18, 8, "Unit", border=1, ln=False, fill=True, align="C")
            pdf.cell(20, 8, "Rate (Rs)", border=1, ln=False, fill=True, align="R")
            pdf.cell(25, 8, "Total (Rs)", border=1, ln=True, fill=True, align="R")
            
            # Table Body
            pdf.set_font("Helvetica", "", 9)
            row_height = 7
            for i, item_obj in enumerate(st.session_state.quote_items, 1):
                desc = item_obj["particulars"]
                qty_val = f"{item_obj['qty']:.2f}"
                unit_val = item_obj["unit"]
                rate_val = f"{item_obj['rate']:,}"
                total_val = f"{item_obj['total']:,.2f}"
                
                # Check for table page overflow and wrap text description nicely
                # For safety, let's truncate description slightly if it exceeds 45 chars to keep it in 1 row on PDF
                if len(desc) > 45:
                    desc = desc[:42] + "..."
                    
                pdf.cell(12, row_height, str(i), border=1, ln=False, align="C")
                pdf.cell(95, row_height, desc, border=1, ln=False, align="L")
                pdf.cell(20, row_height, qty_val, border=1, ln=False, align="R")
                pdf.cell(18, row_height, unit_val, border=1, ln=False, align="C")
                pdf.cell(20, row_height, rate_val, border=1, ln=False, align="R")
                pdf.cell(25, row_height, total_val, border=1, ln=True, align="R")
                
            pdf.ln(4)
            
            # Totals Calculations block aligned right
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(130, 6, "", ln=False)
            pdf.cell(35, 6, "Subtotal:", ln=False, align="R")
            pdf.cell(25, 6, f"Rs. {subtotal:,.2f}", ln=True, align="R")
            
            if add_gst:
                pdf.cell(130, 6, "", ln=False)
                pdf.cell(35, 6, "GST (18%):", ln=False, align="R")
                pdf.cell(25, 6, f"Rs. {gst_amt:,.2f}", ln=True, align="R")
                
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(130, 8, "", ln=False)
            pdf.cell(35, 8, "GRAND TOTAL:", border="TB", ln=False, align="R")
            pdf.cell(25, 8, f"Rs. {grand_total:,.2f}", border="TB", ln=True, align="R")
            
            pdf.ln(10)
            
            # Notes / Terms block
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 5, "Terms & Conditions:", ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(0, 4, "1. All itemized material requirements scale proportionally based on actual site measurements.", ln=True)
            pdf.cell(0, 4, "2. If payment is made via online bank transfer/transaction, 18% GST will be extra.", ln=True)
            pdf.cell(0, 4, "3. Quotation is valid for 30 days from the date of issue.", ln=True)
            
            pdf.ln(15)
            # Signature Area
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(130, 5, "", ln=False)
            pdf.cell(0, 5, "For Vastu Decor", ln=True, align="C")
            pdf.ln(10)
            pdf.cell(130, 5, "", ln=False)
            pdf.cell(0, 5, "Authorized Signatory", border="T", ln=True, align="C")
            
            return pdf.output()
            
        try:
            pdf_out = create_pdf_bytes()
            st.download_button(
                label="📥 Download Professional PDF Invoice",
                data=bytes(pdf_out),
                file_name=f"Vastu_Decor_Quotation_{client_name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error compiling PDF: {e}")
