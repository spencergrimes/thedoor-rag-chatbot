# 🤖 Claude Code Memory: The Door RAG Chatbot

## 📋 Project Overview
**Repository**: https://github.com/spencergrimes/thedoor-rag-chatbot  
**Live Demo**: https://huggingface.co/spaces/sgrimes/thedoor-rag-chatbot  
**Current Status**: Functional RAG chatbot with basic Streamlit interface

## 🎯 Current Task: Gemini-Style UI Redesign

### 🎨 Gemini UI Characteristics to Implement

#### **Visual Design**
- **Clean, minimal interface** with lots of white space
- **Rounded corners** on all elements (12px+ border radius)
- **Subtle shadows** and gradients for depth
- **Modern typography**: Google Sans/Inter font family
- **Color scheme**: Blue accent (#1a73e8), light grays, clean whites

#### **Layout Structure**
```
┌─────────────────────────────────────────┐
│ Header: Logo + Title + Settings         │
├─────────────────────────────────────────┤
│ Main Chat Area:                         │
│ ┌─────────────────────────────────────┐ │
│ │ Message bubbles with clean styling │ │
│ │ User: Right-aligned, blue bg       │ │
│ │ AI: Left-aligned, light gray bg    │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ Suggested Prompts (chips)               │
├─────────────────────────────────────────┤
│ Input Box: Rounded, with send button   │
└─────────────────────────────────────────┘
```

#### **Interactive Elements**
- **Suggested prompt chips**: Clickable pills with common questions
- **Typing indicators**: Animated dots while AI responds
- **Response actions**: Copy, thumbs up/down, regenerate
- **Smooth animations**: Fade-ins, slide-ups for new messages
- **Message formatting**: Structured responses with headers, bullets

### 🛠️ Technical Implementation Plan

#### **1. UI Framework Updates**
```python
# Enhanced Streamlit with custom CSS
st.markdown("""
<style>
/* Gemini-style custom CSS */
.main-container { 
    font-family: 'Google Sans', 'Inter', sans-serif;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}
.chat-message {
    border-radius: 16px;
    padding: 16px 20px;
    margin: 8px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.user-message {
    background: #1a73e8;
    color: white;
    margin-left: 20%;
}
.ai-message {
    background: #f8f9fa;
    border: 1px solid #e8eaed;
}
</style>
""", unsafe_allow_html=True)
```

#### **2. Response Formatting** 
```python
def format_gemini_response(answer, sources, confidence):
    return f"""
    <div class="gemini-response">
        <div class="response-content">{answer}</div>
        <div class="response-meta">
            <span class="confidence">Confidence: {confidence:.0%}</span>
            <span class="sources">{len(sources)} sources</span>
        </div>
        <div class="response-actions">
            <button class="action-btn">📋 Copy</button>
            <button class="action-btn">👍</button>
            <button class="action-btn">👎</button>
        </div>
    </div>
    """
```

#### **3. Suggested Prompts System**
```python
SUGGESTED_PROMPTS = [
    "What time are Sunday services?",
    "How can I get involved?", 
    "What is The Door's mission?",
    "Where is the church located?",
    "What programs do you offer?"
]

def render_prompt_chips():
    cols = st.columns(len(SUGGESTED_PROMPTS))
    for i, prompt in enumerate(SUGGESTED_PROMPTS):
        with cols[i]:
            if st.button(prompt, key=f"prompt_{i}"):
                return prompt
```

#### **4. Enhanced Message Display**
```python
def display_message(role, content, sources=None, confidence=None):
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        # AI message with Gemini-style formatting
        with st.container():
            st.markdown(content)
            if sources:
                with st.expander("📚 Sources", expanded=False):
                    for source in sources:
                        st.write(f"• **{source['title']}** ({source['similarity']:.0%} match)")
```

### 🎨 Color Palette & Typography
```css
:root {
    --primary-blue: #1a73e8;
    --light-blue: #e8f0fe;
    --text-primary: #202124;
    --text-secondary: #5f6368;
    --background: #fafafa;
    --surface: #ffffff;
    --border: #e8eaed;
    --shadow: 0 1px 6px rgba(32,33,36,.28);
}
```

### 📱 Responsive Design Considerations
- **Mobile-first**: Touch-friendly buttons (44px min height)
- **Flexible layout**: Adapts to different screen sizes
- **Readable text**: 16px+ font size, good contrast
- **Thumb zones**: Important actions within easy reach

## 🔧 Technical Stack Status

### **Current Implementation**
- ✅ **Backend**: Fully functional RAG pipeline
- ✅ **Data**: Web scraping, vector storage, embeddings
- ✅ **LLM Integration**: Ollama (gemma:2b) + OpenAI fallback
- ✅ **Basic UI**: Streamlit chat interface
- ✅ **Deployment**: GitHub + Hugging Face Spaces ready

### **Files to Modify**
```
src/chatbot/app.py           # Main Streamlit interface
app.py                       # Root app for HF Spaces  
requirements.txt             # May need additional UI packages
static/style.css             # New: Custom CSS file
static/script.js             # New: Custom JavaScript
```

### **Dependencies to Add**
```txt
streamlit-chat               # Better chat components
streamlit-elements           # Advanced UI elements  
plotly                       # For confidence visualizations
streamlit-option-menu        # Modern navigation
```

## 🎯 Success Metrics
- **Visual Appeal**: Matches Gemini's clean aesthetic
- **User Experience**: Intuitive, smooth interactions
- **Performance**: Fast response times maintained
- **Mobile Friendly**: Works well on all device sizes
- **Professional**: Portfolio-ready presentation

## 🔄 Next Steps for Continuation
1. **Start with CSS**: Implement custom styling first
2. **Message Components**: Redesign chat message display
3. **Prompt Chips**: Add suggested question buttons
4. **Animations**: Implement smooth transitions
5. **Response Actions**: Add copy/feedback buttons
6. **Mobile Testing**: Ensure responsive design
7. **Performance**: Optimize for smooth interactions
8. **Polish**: Final touches and refinements

## 📝 Development Notes
- **Current Ollama Model**: `gemma:2b` (working)
- **API Endpoints**: Using `/api/generate` (fixed)
- **Caching**: Streamlit caching optimized
- **Error Handling**: Robust fallbacks in place
- **Environment**: Virtual env set up, all dependencies installed

## 🚀 Portfolio Impact
This redesign will transform a functional RAG system into a **visually stunning, production-quality AI application** that demonstrates:
- **Modern UI/UX design skills**
- **Full-stack AI development**
- **Attention to user experience**
- **Professional presentation standards**

Perfect for showcasing to potential employers and clients!