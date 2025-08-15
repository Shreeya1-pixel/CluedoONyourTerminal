# CluedoONyourTerminal

**The Ultimate AI-Powered Murder Mystery Game for Your Terminal**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Terminal](https://img.shields.io/badge/Platform-Terminal-black.svg)](https://en.wikipedia.org/wiki/Terminal)

## A Dark Night at Blackwood Manor

Welcome to **CluedoONyourTerminal** - where classic murder mystery meets cutting-edge AI! You are Detective Inspector James Blackwood, called to investigate a murder at the grand Blackwood Manor estate in 1923.

Each game generates a unique mystery with AI-powered suspects who have realistic personalities, motives, and secrets. Some will tell the truth, others will lie, and some will try to evade your questions. It's up to you to piece together the evidence and identify the killer!

## Features

### AI-Powered Suspects
- **Dynamic Personalities**: Each suspect has unique traits and reliability scores
- **Probabilistic Deception**: Suspects may lie, evade, or tell the truth based on their personality
- **Realistic Responses**: AI generates contextual, natural-sounding answers
- **Memory & Consistency**: The system remembers everything and tracks contradictions

### Advanced Investigation System
- **Knowledge Base**: Maintains ground truth about what actually happened
- **Consistency Engine**: Automatically detects contradictions between statements
- **Suspicion Tracking**: Dynamic suspicion scores that change based on behavior
- **Evidence Analysis**: Physical clues, digital records, and witness testimony

### Immersive Gameplay
- **Procedural Generation**: Every case is unique with different suspects, motives, and timelines
- **Multiple Difficulty Levels**: Easy, Medium, and Hard modes
- **Real-time Analysis**: Get insights into suspect reliability and truth status
- **Classic Detective Experience**: Interrogate, analyze, and solve the case

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Terminal/Command Prompt

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Shreeya1-pixel/CluedoONyourTerminal.git
   cd CluedoONyourTerminal
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the game**
   ```bash
   python play_game.py
   ```

## How to Play

### Basic Commands
```
interrogate <suspect_number>  - Begin questioning a suspect
ask <question>               - Ask the current suspect a question
switch <suspect_number>      - Move to a different suspect
timeline                     - Review the case timeline and events
analysis                     - Analyze all statements for contradictions
accuse <suspect_number>      - Make your final accusation
help                         - Show help menu
quit                         - End the investigation
```

### Investigation Tips
- **Start with basic questions**: "Where were you at 9 PM?"
- **Ask about relationships**: "Did you know the victim?"
- **Check alibis**: "Can anyone confirm your whereabouts?"
- **Look for contradictions** between suspects
- **Pay attention** to nervous behavior and evasive answers
- **Use 'timeline'** to understand the sequence of events
- **Use 'analysis'** to see who might be lying

### Sample Terminal Session
```
Detective > interrogate 1
Now interrogating: Person person_0
Ask questions using 'ask <your question>'

Detective > ask Where were you at 9 PM?
Question: Where were you at 9 PM?
Response: I was in the library... (nervously)
Insights:
   Reliability: 0.45
   Truth Status: LIE
   Contradictions: 0
   Corroborations: 0

Detective > switch 2
Now interrogating: Person person_1

Detective > ask Where were you at 9 PM?
Question: Where were you at 9 PM?
Response: I was in the kitchen preparing dinner.
Insights:
   Reliability: 0.78
   Truth Status: TRUE
   Contradictions: 0
   Corroborations: 0

Detective > timeline
CASE TIMELINE:
   6:00 PM: Person person_0 was in the library
   7:30 PM: Person person_1 was in the kitchen
   9:00 PM: MURDER OCCURRED in the library
   10:15 PM: Person person_2 discovered the body

Detective > accuse 1
Making accusation against: Person person_0
CONGRATULATIONS! You solved the case!
The murderer was indeed Person person_0!
Final Score: 85
```

## Technical Architecture

### Core Modules
- **`case_generator.py`**: Procedural case generation with validation
- **`knowledge_base.py`**: Central truth store and consistency checker
- **`lie_model.py`**: AI-powered deception system using machine learning
- **`nlp_pipeline.py`**: Natural language processing for question understanding
- **`response_planner.py`**: Orchestrates truth retrieval and response generation
- **`surface_realizer.py`**: Converts structured responses to natural language
- **`game_engine.py`**: Main game orchestrator and state management

### Data Models
- **`models.py`**: Pydantic models for all game entities (Person, Location, Event, etc.)
- **Type Safety**: Custom type aliases for PersonId, LocationId, WeaponId, etc.
- **Validation**: Comprehensive data validation and consistency checking

### AI Components
- **Lie Model**: Uses scikit-learn LogisticRegression for probabilistic deception decisions
- **NLP Pipeline**: Rule-based intent classification with regex patterns
- **Consistency Engine**: Temporal and causal constraint checking
- **Response Planning**: Multi-stage response generation with truth/lie/evasion options

## Testing

The game includes comprehensive testing strategies:
- **Unit Tests**: Individual module functionality
- **Integration Tests**: Module interaction testing
- **Property-Based Tests**: Automated case generation validation
- **Golden Case Tests**: Known scenarios for regression testing

### Quick System Test
```bash
python test_game.py
```
This runs a complete system check to verify all components are working properly.

## Customization

### Adding New Content
- **Suspects**: Add new person templates in `case_generator.py`
- **Locations**: Extend location templates for more variety
- **Weapons**: Add new weapon types and descriptions
- **Questions**: Extend the NLP pipeline for new question types

### Difficulty Levels
- **Easy**: Fewer suspects, more clues, simpler timeline
- **Medium**: Balanced challenge with moderate complexity
- **Hard**: More suspects, fewer clues, complex relationships

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the classic board game Cluedo/Clue
- Built with modern Python and AI technologies
- Designed for terminal enthusiasts and mystery lovers

## Bug Reports

Found a bug? Please open an issue with:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)

## Future Features

- [ ] Web interface version
- [ ] Multiplayer support
- [ ] Custom case editor
- [ ] Advanced AI personalities
- [ ] Mobile app version
- [ ] Discord bot integration

---

**Ready to solve the mystery? Start your investigation now!**

```bash
python play_game.py
```
