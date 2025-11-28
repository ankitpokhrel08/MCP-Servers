# MCP Multi-Server Chat

A smart chatbot that connects multiple AI tools through Model Context Protocol (MCP) servers. Talk to it in plain English, and it can do math, manage expenses, and create animations for you.

## What This Does

This project creates a chat interface that can:

- **Math Operations**: Add, subtract, multiply, divide, calculate powers, and more `Local`
- **Expense Management**: Track expenses, view summaries, and manage your spending `Remote`
- **Animation Creation**: Generate mathematical animations using Manim `Local through Github Cloned Repo`

## Demo
![Demo](demo.mp4)

### Setup Instructions

1. **Clone the repository**

```
git clone <repository-url>
cd MCP_server
```

2. **Install dependencies**

```bash
uv sync
```

3. **Set up your API key**
   Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your-gemini-api-key-here
```

4. **Install Manim (for animations)**
   `https://github.com/abhiemj/manim-mcp-server`

## Running the Application

### Web Interface (Recommended)

```bash
uv run streamlit run streamlit_app.py
```

## Project Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   LangChain      │    │   Gemini API    │
│   Web UI        │◄──►│   MCP Client     │◄──►│   (Google)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────┼────────┐
                       ▼        ▼        ▼
                 ┌──────────┐ ┌──────┐ ┌──────────┐
                 │   Math   │ │Expense│ │  Manim   │
                 │ Server   │ │Server │ │ Server   │
                 │ (Local)  │ │(Remote)│ │(Local)  │
                 └──────────┘ └──────┘ └──────────┘
```

## Testing Your Setup

Try these example prompts:

**Math Testing:**

- "Calculate 25 + 17"
- "What's 15 to the power of 3?"
- "Divide 100 by 4"

**Expense Testing:**

- "Show expense summary"
- "List all expenses"

**Animation Testing:**

- "Create a circle animation"
- "Animate a rotating square"

## Development & Testing

### Testing Individual Components

**Test Math Server:**

```bash
uv run fastmcp run math_server.py
```

### Result
Checkout: [Complex Transformation Animation](https://youtu.be/EOwOC-xqys4?si=x6oZBqcSWprNW0E4) 
Checkout: [Alphabet Manim Animation](https://youtu.be/gsNHnYbNBxI?si=P2BYII4mLirw5qV5)