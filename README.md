# NinjaTrack – Trade Overview Dashboard

A logistics dashboard for managing fruit/produce trade trips — built as a **single-page app** using React (via Babel CDN), Tailwind CSS, and Supabase.

---

## 📁 Files

| File | Purpose |
|------|---------|
| `Trade overview.html` | Main working source file — edit this |
| `index.html` | Production copy pushed to Vercel (keep in sync with above) |
| `Source Load Capture.html` | Standalone dispatch entry / OCR tool |
| `ninjacart-logo.png` | Brand logo embedded in PDF exports |

> **Rule:** Always edit `Trade overview.html`, then copy it to `index.html` before pushing to Git.

---

## 🚀 Deployment

The app is deployed via **Vercel** from the `deploy-trade-overview` Git repository.

```bash
# Sync working file to production copy
cp "Trade overview.html" index.html

# Push to Vercel (auto-deploys on push to main)
cd deploy-trade-overview
git add index.html
git commit -m "Update: <description>"
git push
```

---

## 🗄️ Database (Supabase)

| Table | Purpose |
|-------|---------|
| `trades` | One row per trip. `notes` column stores a JSON envelope (customer assignments + trip notes) |
| `trade_manifest` | Grade-level manifest rows for each trip |
| `expenses` | Destination-side expenses per trip |
| `sales_transactions` | Actual received boxes + sales rate per grade |

### Notes JSON Structure
The `trades.notes` column stores a JSON object — **never a raw string**:
```json
{
  "_customerAssignments": [...],
  "_note": "Freeform trip notes text"
}
```

---

## ✨ Key Features

- **Fleet View** — card grid of all active trips with status badges
- **Detail View** — per-trip manifest, load plan diagram, market reception & sales
- **Customer / DT Assignment** — allocate brands to multiple customers per trip
- **PDF Export** — overall manifest PDF + per-customer manifest PDF (tabbed preview)
- **Source Load Capture** — OCR-assisted dispatch entry tool (separate page)

---

## 🔧 Status Flow

```
IN_TRANSIT → REACHED_MARKET → SALES_STARTED → SALES_COMPLETED → CLOSED
```

> Moving to `REACHED_MARKET` or beyond requires **Destination** + **Arrival Date**.  
> Moving to `SALES_STARTED` or beyond requires at least **one Customer / DT** assigned.

---

## 📦 Tech Stack

- **React 18** (via `unpkg` CDN, compiled by Babel Standalone)  
- **Tailwind CSS** (via CDN)  
- **Supabase JS v2** — database + auth  
- **html2canvas + jsPDF** — PDF/JPG export  
- **Google Fonts** — Inter typeface  

---

## ⚠️ Known Limitations

- **Supabase Storage bucket required** for Trip Media: go to Supabase → Storage → New bucket → name it `trip-media` → make it **Public**. Without this, media uploads will silently fail.
- `MAX_TRUCK_CAPACITY` is hardcoded to `1200` boxes — planned: add a `vehicle_capacity` field in Supabase for per-truck capacities.
