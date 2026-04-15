---
name: schema-markup
description: Add structured data markup for better Google search results.
---

## German Market Override
LocalBusiness Schema fuer deutsche Adressen
Oeffnungszeiten im korrekten deutschen Format
Bewertungen: nur echte, keine gefaelschten
Sprache: "de-DE" in Schema angeben
Pflicht: korrekte Adresse und Telefonnummer

---

# Schema Markup Skill

## Common Schema Types
1. LocalBusiness - for physical locations
2. Organization - for companies
3. Product - for product pages
4. FAQ - for FAQ sections
5. HowTo - for tutorial content
6. Article - for blog posts
7. BreadcrumbList - for navigation

## German-Specific Requirements
- Address format: Strasse, PLZ Stadt, Deutschland
- Phone: +49 format
- Opening hours: Mo-Fr 08:00-17:00
- Language: inLanguage: "de-DE"
- Currency: EUR

## Implementation
- Use JSON-LD format (recommended by Google)
- Test with Google Rich Results Test
- One primary schema per page
- Nest related schemas properly
