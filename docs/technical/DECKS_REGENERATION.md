# Regenerating Presentation Decks

The investor and technical presentation decks are excluded from the repository to keep it lightweight for deployment. If you need to regenerate them:

## Prerequisites
- Node.js installed
- Access to Google Gemini API (for image generation)

## Regeneration Steps

### Investor Deck

```bash
cd investor_deck_v1
npm install
node generate_deck.js
```

This will:
1. Generate slide images using Gemini API
2. Create `IgniteAI_Investor_Deck.pdf`
3. Output HTML version for presentations

### Technical Deck

```bash
cd technical_deck_v1
npm install
node generate_deck.js
```

This will:
1. Generate technical architecture slide images
2. Create `IgniteAI_Technical_Deck.pdf`
3. Output HTML version for presentations

## Manual Creation

If the generation scripts fail, you can also:
1. Use the markdown versions (`investor_deck_v1/deck.md`, `technical_deck_v1/deck.md`)
2. Create slides manually using Google Slides, PowerPoint, or Figma
3. Export as PDF

## Note

These decks are presentation materials and not required for the core application to function. They are gitignored to avoid binary file issues with Hugging Face deployment.
