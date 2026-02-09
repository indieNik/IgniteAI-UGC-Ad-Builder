# 💰 Workflow Usage & Pricing Analysis

**Objective:** Calculate the exact cost for **one 20-second video generation run**.
**Data Source:** `Gemini Developer API pricing _ Gemini API _ Google AI for Developers.html` (Local File).
**Models Used:**
- **Video:** `veo-3.1-fast-generate-preview` (Veo 3.1 Fast)
- **Image:** `imagen-4.0-generate-001` (Imagen 4 Standard)
- **LLM:** `gemini-2.5-flash-image` (Gemini 2.0 Flash)

---

## 1. Cost Breakdown (Per 20s Video Run)

A 20s ad consists of **4 Scenes** (5s each).
*Note: We generate ~6s per scene to ensure coverage, totaling **24s of generated footage**.*

| Component | Usage | Unit Price | Cost (USD) |
| :--- | :--- | :--- | :--- |
| **1. Video Generation** | 24 seconds (Raw) | **$0.15** / second | **$3.60** |
| **2. Image Generation** | 5 Images (4 Scenes + End Card) | **$0.04** / image | **$0.20** |
| **3. LLM Logic** | ~10k Tokens | ~$0.50 / 1M tokens | **< $0.01** |
| **4. Voiceover (External)** | ~1000 characters | ~$0.30 / 1k chars | **$0.30** |
| **TOTAL** | | | **~$4.11** |

---

## 2. Pricing Reference (From Documentation)

### 🎥 Video Generation (Veo 3.1)
| Tier | Price |
| :--- | :--- |
| **Veo 3.1 Fast** | **$0.15** per second |
| **Veo 3.1 Standard** | **$0.40** per second |

### 🖼️ Image Generation (Imagen 4)
| Tier | Price |
| :--- | :--- |
| **Imagen 4 Fast** | **$0.02** per image |
| **Imagen 4 Standard** | **$0.04** per image |
| **Imagen 4 Ultra** | **$0.06** per image |

### 🧠 LLM (Gemini 2.0 Flash)
| Tier | Input Cost | Output Cost |
| :--- | :--- | :--- |
| **Paid** | **$0.10 - $0.50** / 1M | **$0.40** / 1M |
| **Free** | $0.00 | $0.00 |

---

## 3. Optimization Recommendations
To reduce the **$4.11/video** cost:
1.  **Reduce Footage:** Generate exact duration (5s) instead of 6s. (Saves ~$0.60).
2.  **Use Static Images:** Mix static slides (Imagen @ $0.04) with video scenes.
3.  **Use Veo 2.0:** Use `veo-2.0` if pricing is lower (often unlisted or cheaper/free in preview).

---

## 4. Pricing Strategy & Value Proposition

Our pricing is based on a **Value-Based Strategy** rather than strict cost-plus.

- **Starter ($49)**: Ideal for small brands testing the waters. Each video costs ~$4.90, providing a 10x savings compared to traditional studio production.
- **Growth ($149)**: Optimized for scaling. Cost per video drops to ~$2.98, maximizing ROI for active advertisers.

**Why the margin?** 
The gap between COGS (~$4.11) and retail price covers platform maintenance, character consistency fine-tuning (Visual DNA™), and the "Guaranteed Success" fallback architecture which incurs higher costs during primary model outages.
