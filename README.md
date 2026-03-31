# Health AI: Multimodal Medical Awareness Assistant

Health AI is a sophisticated AI-powered health awareness and symptom interpretation platform. It combines a state-of-the-art **Multimodal AI engine** (OpenAI gpt-4o-mini) with robust medical guardrails to provide users with immediate, context-aware information about their health concerns through text, images, and voice.

---

## Key Features

###  Multimodal AI Intelligence
- **Vision Integration:** Upload medical images (symptoms, skin conditions, reports) for AI-powered visual analysis.
- **Contextual Memory:** The chatbot retains history of previous turns within a session, allowing for follow-up questions like *"What about that second symptom?"* or *"How does that affect my diet?"*.
- **Emergency Detection:** Built-in safety logic instantly identifies critical medical emergencies and provides immediate life-saving directives.

### 🎙️ Advanced Text-to-Speech (TTS)
- **Fluid Playback:** Sophisticated text chunking ensures stable, buffer-free reading of long AI responses.
- **Multilingual Support:** Native language detection for English and **Hindi**, utilizing high-quality system voice packs.
- **Interactive Controls:** Pause, Resume, and Stop controls for a refined listening experience.

### 📱 Premium User Experience
- **Responsive Navigation:** A modern, mobile-optimized sidebar with a slide-in Hamburger menu for seamless session management on any device.
- **Persistent History:** Secure session management via Supabase ensure your health history is saved and accessible across devices.
- **Glassmorphism UI:** Built with Tailwind CSS and Framer Motion for smooth, premium micro-animations and transitions.

---

## 🛠️ Technology Stack

### Frontend
- **Framework:** [Next.js](https://nextjs.org/) (App Router)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **Animations:** [Framer Motion](https://www.framer.com/motion/)
- **State & Auth:** [Supabase Auth & Database](https://supabase.com/)

### Backend
- **Engine:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **AI Model:** [OpenAI gpt-4o-mini](https://platform.openai.com/)
- **Security:** [SlowAPI](https://pypi.org/project/slowapi/) (Rate limiting), Audit Middleware
- **Storage:** Supabase Storage (Secure medical image handling)

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.9+
- Node.js 18+
- [Supabase Project](https://supabase.com/)
- [OpenAI API Key](https://platform.openai.com/api-keys)

### 2. Environment Configuration
Create a `.env` file in the root and configure both frontend and backend:

**Backend (`backend/.env`):**
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_key
```

**Frontend (`frontend/.env.local`):**
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Run the Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## ⚠️ Medical Disclaimer

**Health AI is for health awareness and educational purposes only.** It is **not** a diagnostic tool and does **not** provide professional medical advice, treatments, or prescriptions.

1. **NO DIAGNOSIS:** Under no circumstances will this AI provide a definitive medical diagnosis.
2. **CONSULT A DOCTOR:** Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
3. **EMERGENCIES:** If you are experiencing a medical emergency, call your local emergency services (e.g., 911) or go to the nearest emergency room immediately.

---
