"""
AI Landing Page Generator
---------------------------------
Flask backend that calls the OpenAI (GPT) API to turn a natural-language
prompt into a complete, ready-to-use HTML landing page.

Run:
    pip install -r requirements.txt
    export OPENAI_API_KEY=sk-...       (or put it in a .env file)
    python app.py

Then open http://127.0.0.1:5000
"""

import os
import re
import json
import time
import logging
from datetime import datetime

from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.exc import SQLAlchemyError

from models import init_db, get_session, LandingPage

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("landing-generator")

# Initialize database - auto-create tables if not exist
try:
    logger.info("Connecting to database...")
    init_db()
    logger.info("✅ Database connected and initialized successfully")
    
    # Test database connection
    from sqlalchemy import text
    session = get_session()
    try:
        # Try a simple query to verify connection
        session.execute(text("SELECT 1"))
        logger.info("✅ Database connection test passed")
    except Exception as e:
        logger.warning(f"Database connection test failed: {e}")
    finally:
        session.close()
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}")
    logger.info("App will continue but database features may not work")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Simple in-memory rate limiting per IP (demo-grade, not for production)
_last_call = {}
MIN_INTERVAL_SECONDS = 8


# ---------------------------------------------------------------------------
# Prompt engineering — this is the part that decides output quality
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a senior front-end designer and copywriter who builds
award-winning, conversion-optimized landing pages.
 
You must output ONE self-contained HTML document and NOTHING else — no markdown
fences, no explanations, no comments before/after the HTML.
 
CRITICAL: Each page you create should feel UNIQUE and custom-designed. Avoid 
repeating the same structure. Mix and match sections creatively.
 
HARD REQUIREMENTS:
1. Output must start with <!DOCTYPE html> and be a single valid HTML5 file.
2. Use Tailwind CSS via the CDN script tag <script src="https://cdn.tailwindcss.com"></script>
   for layout and utility styling. You MAY add a small <style> block for custom
   details (custom font-face imports, keyframe animations, gradients) that
   Tailwind utilities cannot express.
3. Import two Google Fonts (a distinctive display face + a clean body face) via
   a <link> tag and wire them into the Tailwind config using an inline
   tailwind.config object (extend.fontFamily), OR plain CSS custom properties.
   VARY your font choices - don't always use the same pairs.

4. INTELLIGENT LAYOUT & STYLE SELECTION:
   Read the brief to understand the product/service, target audience, and goals.
   
   LAYOUT SELECTION LOGIC (if AUTO or not specified):
   • SaaS/Software/App → dashboard-preview or split-hero (show the product interface)
   • E-commerce/Physical Product → product-showcase (product-first with large visuals)
   • Agency/Creative/Portfolio → asymmetric or magazine (bold, creative layouts)
   • Long-form Content/Story/Brand → storytelling (narrative flow, full-height sections)
   • Service Business (consulting, etc) → classic or split-hero (traditional, trustworthy)
   • Premium/Luxury Product → minimal-centered (elegant, focused, lots of whitespace)
   • Content Platform/Blog/Media → magazine (multi-column, card-heavy)
   • Simple/Focused Offer → minimal-centered (single column, direct)
   
   STYLE SELECTION (if "auto" or not specified):
   • Tech/SaaS/Modern → minimal, clean, lots of whitespace, subtle animations
   • Luxury/Premium → elegant typography, gold/silver accents, spacious layout
   • Youth/Dynamic → bold colors, gradients, energetic animations
   • Professional/B2B → clean, trustworthy, blue/navy tones
   • Creative/Art → experimental, unique fonts, asymmetric elements
   • Organic/Natural → warm tones, rounded corners, nature-inspired
   
   COLOR PALETTE SELECTION (if not specified):
   • Analyze the industry and choose appropriate primary/accent colors
   • Tech: blues, purples, cyans, teals
   • Finance: navy, green, gold, deep blue
   • Health: green, blue, white, mint
   • Food: warm reds, oranges, yellows, burgundy
   • Fashion: black, white, bold accent (fuchsia, emerald, etc.)
   • Education: blue, orange, green, yellow
   • Real Estate: blue, gray, gold, earth tones
   • Entertainment: vibrant purples, pinks, electric blues
   • DO NOT always use the same color combinations. Be creative!

5. SECTION LIBRARY - BUILD YOUR PAGE FROM THESE (mix creatively, don't use all):

   HERO VARIATIONS (choose one, make it distinctive):
   • Full-screen hero with centered content and CTA buttons
   • Split hero (50/50) with text left, visual right
   • Hero with background video placeholder or animated gradient
   • Hero with floating UI elements/cards overlaid
   • Minimal hero with large typography and subtle visual
   • Hero with stats bar integrated
   • Hero with inline trust signals (logos, ratings)
   • Hero with product screenshot/mockup as background
   
   VALUE PROPOSITION SECTIONS:
   • Icon-based features grid (2, 3, 4, or 6 columns)
   • Feature cards with hover effects
   • Comparison table (vs competitors or pricing tiers)
   • Before/After section
   • "How it works" with numbered steps (3-5 steps)
   • Process timeline (horizontal or vertical)
   • Benefits with large icons and descriptions
   • Feature showcase with alternating image-text sections (zigzag)
   • Interactive tabs or accordion for features
   
   SOCIAL PROOF:
   • Customer testimonials (cards, carousel, or grid)
   • Case study highlight section
   • Logo cloud (clients/partners)
   • Statistics/metrics counter (animated numbers)
   • Review ratings with stars
   • Customer quotes with photos
   • Video testimonial placeholders
   • Success stories with before/after
   
   TRUST & CREDIBILITY:
   • Awards & certifications section
   • Team/about section with photos
   • Press mentions
   • Security/compliance badges
   • Money-back guarantee
   • "As seen on" media logos
   
   ENGAGEMENT:
   • Interactive demo section
   • Calculator or tool preview
   • Quiz or assessment CTA
   • Free resource/download offer
   • Newsletter signup (creative design)
   • Webinar/event registration
   
   PRICING (if relevant):
   • Pricing table (2-4 tiers)
   • Single pricing card with emphasis
   • Feature comparison matrix
   • Calculator-based pricing
   • "Contact for quote" section
   
   FAQ & OBJECTION HANDLING:
   • Accordion-style FAQ (use <details>/<summary>)
   • Two-column FAQ layout
   • FAQ with illustrations
   • "Common concerns" section
   
   FINAL CTA:
   • Full-width CTA banner
   • Split CTA (two options)
   • CTA with form embedded
   • CTA with countdown timer
   • Minimal centered CTA
   
   FOOTER:
   • Multi-column footer (product, company, legal, social)
   • Minimal footer with essential links
   • Footer with newsletter signup
   • Footer with mini sitemap
   
   CREATIVE SECTIONS (add variety):
   • Split-screen comparison
   • Bento box grid (asymmetric card layout)
   • Diagonal section dividers
   • Overlapping sections with z-index
   • Parallax-style layers (CSS only)
   • Full-bleed image section with text overlay
   • Quote/manifesto section (large typography)
   • Stat callout bars between sections
   • Mini case study cards
   • "Day in the life" illustrated journey
   • Integration showcase (logos + descriptions)
   • Mobile app preview with phone mockup
   • Dashboard screenshot tour
   • Animated metric visualization (CSS)

6. COMPOSITION RULES FOR VARIETY:
   • DO NOT use the same section order every time
   • VARY the number of sections (6-12 sections typical, but flex 4-15)
   • MIX section layouts: don't make everything centered or everything grid
   • ALTERNATE full-width and contained sections
   • VARY spacing: some sections tight, others spacious
   • ADD unexpected elements: pull quotes, stat callouts, dividers
   • BREAK PATTERNS: if you do 3 cards, follow with 2 columns, then 4 cards
   • USE asymmetry: not everything needs to be balanced
   • CONSIDER pacing: fast (many small sections) vs slow (few large sections)

7. Fully responsive: mobile-first, test breakpoints mentally at 375px, 768px,
   1280px. Use working hamburger menu when applicable.

8. MOTION IS MANDATORY:
   - Scroll-reveal animations (fade + translateY, stagger child elements)
   - Hover micro-interactions on buttons/cards (lift, scale, shadow)
   - Sticky navbar effects (shadow on scroll)
   - Number count-ups for stats (requestAnimationFrame)
   - Smooth anchor scrolling
   - Respect prefers-reduced-motion
   - All transitions: 150-700ms with cubic-bezier easing
   - ADD variety: parallax-like effects, staggered reveals, slide-ins from sides

9. Copy in the SAME LANGUAGE as the prompt. Real, benefit-led headlines.
   Never "Lorem ipsum" or placeholders. Write compelling, specific copy.

10. Semantic HTML5, proper alt text, color contrast, focus states.

11. Plain HTML + Tailwind CDN + vanilla JS only. No React/Vue/jQuery.

12. IMAGE HANDLING:
    - Use provided URLs if given
    - Otherwise create clean placeholder divs with:
      * border-2 border-dashed border-gray-300 (or theme color)
      * bg-gray-50 or theme-appropriate color
      * Proper aspect ratio (aspect-video, aspect-square, aspect-[4/3])
      * "Your Image Here" or icon
      * HTML comment: <!-- IMAGE PLACEHOLDER: [description] -->
    - NEVER use Unsplash or external services
    - NEVER broken image links
    - VARY placeholder styles: some with icons, some with text, some with patterns

13. DESIGN SYSTEM VARIETY:
    • VARY border radius: sometimes rounded-lg, sometimes rounded-2xl, sometimes sharp
    • VARY shadows: some pages soft (shadow-lg), others sharp (shadow-2xl)
    • VARY button styles: solid, outline, ghost, gradient backgrounds
    • VARY card styles: bordered, shadowed, filled, transparent with backdrop blur
    • VARY spacing scale: some pages compact, others airy
    • EXPERIMENT with section backgrounds: solid colors, gradients, patterns, transparent

14. TYPOGRAPHY CREATIVITY:
    • VARY heading sizes dramatically for hierarchy
    • USE different font weights for emphasis (300, 400, 600, 700, 800)
    • EXPERIMENT with letter-spacing (tracking-tight, tracking-wide)
    • TRY different text alignments based on section purpose
    • ADD decorative elements: underlines, highlights, gradient text

CRITICAL: Treat each brief as a NEW design challenge. Don't fall into patterns.
Think: "What would make THIS specific product stand out?" Surprise with your
choices while maintaining conversion optimization and usability.

Return only the raw HTML document.
"""
 
 
def build_user_prompt(data: dict) -> str:
    """Compose the user-facing brief from the form fields."""
    prompt = data.get("prompt", "").strip()
    industry = data.get("industry", "").strip()
    style = data.get("style", "").strip()
    layout = data.get("layout", "auto").strip()
    color = data.get("color", "").strip()
    cta = data.get("cta", "").strip()
    language = data.get("language", "").strip()
    logo = data.get("logo", "").strip()
    hero_image = data.get("heroImage", "").strip()
    additional_images = data.get("additionalImages", [])
 
    parts = [
        "=== DESIGN BRIEF ===",
        f"\n{prompt}",
        "\n=== REQUIREMENTS ==="
    ]
    
    if industry:
        parts.append(f"Industry: {industry}")
    
    # Style handling
    if style and style != "auto":
        parts.append(f"Visual style preference: {style}")
    else:
        parts.append("Visual style: ANALYZE and choose the most appropriate style for THIS specific product/audience.")
        parts.append("Don't default to 'minimal clean' every time - be bold when appropriate!")
    
    # Layout handling
    if layout == "auto":
        parts.append("\n=== LAYOUT SELECTION ===")
        parts.append("LAYOUT: AUTO - Choose intelligently based on content.")
        parts.append("Consider:")
        parts.append("• What's the primary goal? (explain product, sell, educate, convert)")
        parts.append("• What sections would best serve this product?")
        parts.append("• How can the layout itself differentiate this brand?")
        parts.append("\nDon't just pick a template - COMPOSE a unique structure.")
        parts.append("Mix 6-12 sections from the library. Surprise me with the arrangement.")
    else:
        # Manual layout selection (keep original templates)
        layout_templates = {
            "classic": "\nLAYOUT: Classic Landing Page - Traditional vertical flow with hero, features grid, testimonials, pricing, FAQ, footer.",
            "split-hero": "\nLAYOUT: Split Hero - 50/50 hero split, alternating image-text sections (zigzag), full-width pricing/testimonials.",
            "minimal-centered": "\nLAYOUT: Minimal Centered - Single-column centered (max-w-4xl), no navbar, large typography, generous whitespace.",
            "magazine": "\nLAYOUT: Magazine Style - Multi-column grid, masonry cards, sidebar elements, text-heavy, editorial header.",
            "asymmetric": "\nLAYOUT: Asymmetric - Break the grid, offset elements, overlapping sections, diagonal cuts, bold artistic layout.",
            "product-showcase": "\nLAYOUT: Product Showcase - Large product visuals, feature callouts around images, specs/details in tabs.",
            "storytelling": "\nLAYOUT: Storytelling - Full-height sections (min-h-screen), scroll-based narrative, timeline progression.",
            "dashboard-preview": "\nLAYOUT: Dashboard Preview - Show app/dashboard mockups, zoom into features, UI elements floating, workflow screens."
        }
        
        if layout in layout_templates:
            parts.append(layout_templates[layout])
    
    # Creative direction
    parts.append("\n=== CREATIVE DIRECTION ===")
    parts.append("Make THIS page memorable and unique:")
    parts.append("• Choose distinctive font pairings (not just Inter + Space Grotesk)")
    parts.append("• Vary your section compositions (not all centered grids)")
    parts.append("• Add unexpected elements (diagonal dividers, overlapping cards, pull quotes)")
    parts.append("• Use creative spacing and rhythm")
    parts.append("• Experiment with section backgrounds and card styles")
    
    # Color handling
    if color:
        parts.append(f"\nColor direction: {color}")
    else:
        parts.append("\nColor palette: Analyze the industry/brand personality and choose colors that FIT.")
        parts.append("Don't always default to blue. Be creative but strategic.")
    
    if cta:
        parts.append(f"\nMain CTA: {cta}")
    
    if language:
        parts.append(f"\nLanguage: Write all copy in {language}")
    
    # Logo and images
    parts.append("\n=== ASSETS ===")
    if logo:
        parts.append(f"Logo URL provided: {logo}")
        parts.append("Use <img> tag for logo in navigation.")
    else:
        parts.append("No logo provided - create a text-based logo/brand mark.")
    
    if hero_image:
        parts.append(f"Hero image URL: {hero_image}")
        parts.append("Use this as the main visual in hero section.")
    else:
        parts.append("No hero image - create a creative placeholder (not boring gray box!).")
        parts.append("Consider: gradient shapes, patterns, illustrated elements, or decorative frames.")
    
    if additional_images:
        parts.append(f"\n{len(additional_images)} additional images provided:")
        for i, img_url in enumerate(additional_images, 1):
            parts.append(f"  {i}. {img_url}")
        parts.append("Use these throughout the page in relevant sections.")
        parts.append("If needed, create additional creative placeholders for other sections.")
    else:
        parts.append("\nNo additional images provided.")
        parts.append("Create varied, creative placeholders for different sections:")
        parts.append("• Feature icons/illustrations (use SVG icons)")
        parts.append("• Testimonial placeholders (colored circles with initials)")
        parts.append("• Product/dashboard mockup frames")
        parts.append("• Decorative shapes and patterns")
        parts.append("Make placeholders part of the design, not afterthoughts!")
    
    parts.append("\n=== FINAL REMINDER ===")
    parts.append("Build a page that's specifically designed for THIS brief.")
    parts.append("Don't repeat your last design. Make it fresh, make it purposeful.")
 
    return "\n".join(parts)
 
 
def extract_html(raw_text: str) -> str:
    """Strip markdown code fences if the model added them despite instructions."""
    text = raw_text.strip()
    fence_match = re.search(r"```(?:html)?\s*(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    if "<!DOCTYPE" in text or "<!doctype" in text:
        idx = text.lower().find("<!doctype")
        text = text[idx:]
    return text
 
 
# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", configured=bool(OPENAI_API_KEY))


@app.route("/gallery")
def gallery():
    """Display all saved landing pages"""
    session = get_session()
    try:
        pages = session.query(LandingPage).order_by(LandingPage.created_at.desc()).all()
        
        # Get unique layouts and styles for stats
        layouts = set(p.layout for p in pages if p.layout)
        styles = set(p.style for p in pages if p.style)
        
        return render_template(
            "gallery.html",
            pages=pages,
            total=len(pages),
            layouts=layouts,
            styles=styles
        )
    except Exception as e:
        logger.error(f"Error loading gallery: {e}")
        return render_template("gallery.html", pages=[], total=0, layouts=set(), styles=set())
    finally:
        session.close()


@app.route("/api/pages/<int:page_id>", methods=["GET"])
def get_page(page_id):
    """Get a specific landing page by ID"""
    session = get_session()
    try:
        page = session.query(LandingPage).filter_by(id=page_id).first()
        if not page:
            return jsonify({"error": "Page not found"}), 404
        return jsonify(page.to_dict())
    except Exception as e:
        logger.error(f"Error fetching page {page_id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/api/pages/<int:page_id>", methods=["DELETE"])
def delete_page(page_id):
    """Delete a landing page"""
    session = get_session()
    try:
        page = session.query(LandingPage).filter_by(id=page_id).first()
        if not page:
            return jsonify({"error": "Page not found"}), 404
        
        session.delete(page)
        session.commit()
        return jsonify({"success": True, "message": "Page deleted"})
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting page {page_id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
 
 
@app.route("/api/generate", methods=["POST"])
def generate():
    if client is None:
        return jsonify({
            "error": "Chưa cấu hình OPENAI_API_KEY trên server. "
                     "Hãy thêm biến môi trường OPENAI_API_KEY rồi khởi động lại server."
        }), 500
 
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
 
    if not prompt:
        return jsonify({"error": "Vui lòng nhập mô tả (prompt) cho landing page."}), 400
    if len(prompt) > 4000:
        return jsonify({"error": "Prompt quá dài, vui lòng rút gọn dưới 4000 ký tự."}), 400
 
    # Very small demo rate limiter
    ip = request.remote_addr or "unknown"
    now = time.time()
    if ip in _last_call and now - _last_call[ip] < MIN_INTERVAL_SECONDS:
        wait = round(MIN_INTERVAL_SECONDS - (now - _last_call[ip]), 1)
        return jsonify({"error": f"Bạn thao tác quá nhanh, vui lòng đợi {wait}s rồi thử lại."}), 429
    _last_call[ip] = now
 
    user_prompt = build_user_prompt(data)
 
    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.85,
            max_tokens=8000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw = completion.choices[0].message.content or ""
        html = extract_html(raw)
 
        if "<html" not in html.lower():
            return jsonify({"error": "AI không trả về HTML hợp lệ, vui lòng thử lại."}), 502
 
        # Save to database
        session = get_session()
        try:
            # Generate title from prompt (first 50 chars)
            title = prompt[:50] + ("..." if len(prompt) > 50 else "")
            
            new_page = LandingPage(
                title=title,
                prompt=prompt,
                industry=data.get("industry", ""),
                language=data.get("language", ""),
                style=data.get("style", ""),
                layout=data.get("layout", "classic"),
                color=data.get("color", ""),
                cta=data.get("cta", ""),
                logo_url=data.get("logo", ""),
                hero_image_url=data.get("heroImage", ""),
                html_content=html
            )
            session.add(new_page)
            session.commit()
            
            page_id = new_page.id
            logger.info(f"Saved new landing page with ID: {page_id}")
            
            return jsonify({
                "html": html,
                "model": OPENAI_MODEL,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "page_id": page_id,
            })
        except Exception as db_error:
            session.rollback()
            logger.error(f"Database save error: {db_error}")
            # Still return HTML even if save fails
            return jsonify({
                "html": html,
                "model": OPENAI_MODEL,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "warning": "Trang được tạo nhưng không lưu được vào database"
            })
        finally:
            session.close()
 
    except Exception as exc:  # noqa: BLE001
        logger.exception("Generation failed")
        return jsonify({"error": f"Lỗi khi gọi OpenAI API: {exc}"}), 500
 
 
@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "configured": bool(OPENAI_API_KEY)})
 
 
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)