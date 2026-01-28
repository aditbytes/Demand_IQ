# DemandIQ Webpage Prompt

> Use this prompt to generate a stunning, modern, single-page marketing website for the DemandIQ retail demand forecasting system.

---

## Prompt

```
Create a premium, visually stunning single-page marketing website for "DemandIQ" - a retail demand forecasting and replenishment engine.

### Brand Identity
- **Name**: DemandIQ
- **Tagline**: "Turning ML into Money 💰" or "Predict. Restock. Profit."
- **Color Palette**: 
  - Primary: Deep blue (#1a237e) to electric blue (#2979ff) gradient
  - Accent: Vibrant teal (#00bfa5) for CTAs
  - Dark mode default with glassmorphism elements
  - Warning colors: Red (#ff5252) for HIGH risk, Amber (#ffc107) for MED, Green (#69f0ae) for LOW

### Design Style
- Premium SaaS aesthetic with glassmorphism cards
- Smooth scroll animations using GSAP or AOS
- Interactive 3D elements using Three.js (animated globe or data visualization)
- Micro-animations on hover
- Modern typography (Inter or Outfit from Google Fonts)
- Dark gradient backgrounds with subtle animated noise/particles

### Required Sections

1. **Hero Section**
   - Bold headline: "Predict Next-Week Sales. Eliminate Stockouts."
   - Subheadline: "AI-powered demand forecasting that tells store managers exactly how much to reorder."
   - CTA buttons: "Get Started" and "Watch Demo"
   - Animated 3D visualization (rotating data cube or supply chain nodes)
   - Floating stats: "95% Service Level", "30% Less Overstock", "7-Day Forecasts"

2. **Problem Statement**
   - Title: "Retailers Lose Billions to Poor Inventory Management"
   - Pain points with icons:
     - Stockouts = Lost Sales
     - Overstock = Dead Capital
     - Manual Forecasting = Errors
   - Animated counter showing potential savings

3. **How It Works**
   - 4-step animated flow:
     1. "Ingest Sales Data" (CSV/database icon)
     2. "Train ML Models" (Prophet + XGBoost badges)
     3. "Predict Demand" (chart trending up)
     4. "Generate Reorders" (clipboard with checkmarks)
   - Connecting animated lines between steps

4. **Features Grid**
   - 6 feature cards with hover effects:
     - 📈 Multi-Model Forecasting (Prophet, XGBoost, Baseline)
     - 🔔 Smart Alerts (HIGH/MED/LOW risk classification)
     - 📊 Interactive Dashboard (Streamlit-powered)
     - ⚡ Real-Time API (FastAPI endpoints)
     - 📦 Safety Stock Calculator (Z-score formula)
     - 🧪 MLflow Tracking (experiment management)

5. **Tech Stack**
   - Animated tech logo carousel or grid:
     - Python, Pandas, NumPy
     - Prophet, XGBoost
     - FastAPI, Streamlit
     - Plotly, MLflow
   - "Built with FAANG-level engineering standards"

6. **Dashboard Preview**
   - Large mockup/screenshot of Streamlit dashboard
   - Highlighted features with callout badges:
     - Sales history chart
     - Forecast curve overlay
     - Risk-classified reorder recommendations
   - "See your inventory health at a glance"

7. **API Documentation**
   - Code snippet cards showing endpoints:
     - GET /forecast/{store_id}/{sku}
     - GET /reorder/{store_id}/{sku}
     - GET /alerts?risk_level=HIGH
   - Syntax-highlighted JSON response examples
   - "RESTful API. Auto-generated docs."

8. **The Math Behind It**
   - Elegant formula displays:
     - Safety Stock = Z × σ × √(lead_time)
     - Reorder Qty = Forecast + Safety Stock - Current Stock
   - Animated visualization showing demand variability
   - "95% service level with minimal overstock"

9. **Use Cases**
   - 3 industry cards:
     - 🛒 Grocery & FMCG
     - 🎮 Electronics & Hobbies
     - 👕 Fashion & Apparel
   - Each with a brief value proposition

10. **Testimonials/Social Proof**
    - Placeholder for future testimonials
    - Trust badges: "MIT Licensed", "Production Ready", "Open Source"

11. **Getting Started**
    - Terminal-style code block showing:
      ```bash
      git clone <repo>
      pip install -r requirements.txt
      python pipelines/ingest.py
      streamlit run dashboard/app.py
      ```
    - "Up and running in 5 minutes"

12. **Footer**
    - Links: GitHub, Documentation, API Docs, Contact
    - "DemandIQ © 2024 - Turning ML into Money"
    - Social media icons (GitHub, LinkedIn)

### Technical Requirements
- Pure HTML, CSS, JavaScript (no frameworks)
- Mobile responsive
- Smooth 60fps animations
- Lazy loading for images
- SEO optimized with meta tags
- Accessible (WCAG 2.1 AA)

### Interaction Details
- Navbar: Sticky, transparent → solid on scroll
- Parallax scrolling effects
- Number counters animate when in viewport
- Cards have subtle 3D tilt on hover
- Buttons have ripple effect on click
- Sections fade/slide in on scroll

### Optional Enhancements
- Dark/Light mode toggle
- Animated cursor follower
- Floating particles background
- Interactive demo calculator (input demand → show reorder qty)
```

---

## Files to Generate

1. `index.html` - Main HTML structure
2. `styles.css` - Complete CSS design system
3. `script.js` - Animations and interactivity
4. `assets/` - Folder for images, icons, and 3D models

---

## Example Hero Section Code Snippet

```html
<section id="hero" class="hero-section">
  <div class="hero-background">
    <canvas id="three-canvas"></canvas>
    <div class="gradient-overlay"></div>
  </div>
  <div class="hero-content">
    <h1 class="hero-title">
      Predict Next-Week Sales.
      <span class="gradient-text">Eliminate Stockouts.</span>
    </h1>
    <p class="hero-subtitle">
      AI-powered demand forecasting that tells store managers exactly how much to reorder.
    </p>
    <div class="hero-cta">
      <a href="#demo" class="btn btn-primary">Get Started</a>
      <a href="#demo" class="btn btn-secondary">Watch Demo</a>
    </div>
    <div class="hero-stats">
      <div class="stat">
        <span class="stat-value" data-count="95">0</span>%
        <span class="stat-label">Service Level</span>
      </div>
      <div class="stat">
        <span class="stat-value" data-count="30">0</span>%
        <span class="stat-label">Less Overstock</span>
      </div>
      <div class="stat">
        <span class="stat-value" data-count="7">0</span>
        <span class="stat-label">Day Forecasts</span>
      </div>
    </div>
  </div>
</section>
```

---

## Notes for Development

- Prioritize performance: Lazy load Three.js scenes
- Use CSS variables for easy theming
- Implement intersection observer for scroll animations
- Test on mobile devices for touch interactions
- Consider adding a loading screen with DemandIQ logo animation
