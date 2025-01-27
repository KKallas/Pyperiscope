# PyPeriscope
![image](https://github.com/user-attachments/assets/227ad299-eeef-4063-bcbb-c0e0d5be3cb7)

A visual automation framework for Jupyter Lab designed for secure, air-gapped environments. PyPeriscope enables creation, execution, and debugging of GUI automation workflows through visual pattern matching, with local LLM support for intelligent decision making.

## Design Philosophy
PyPeriscope is built for air-gapped automation servers while maintaining accessibility from any device - from cell phones to desktop computers. The tool provides reliable, fault-tolerant workflow recording with built-in state management and error recovery.

Built following [**Simple Software Dogmas**](https://github.com/KKallas/SimpleSoftwareDogmas), PyPeriscope emphasizes simplicity, reliability, and secure automation development.

## Core Components

### Scraper: Visual Element Selection
Define automation targets on the automation server:
```python
from pyperiscope import Scraper
scraper = Scraper(pyautogui.screenshot())
step = scraper.get_scope()  # Interactive selection creates automation step
```

### Scope: Pattern Detection Engine
Handle screen interactions on the automation server:
```python
# Find and interact with screen elements
step.find(confidence=0.9)
if step.found_locations:
    pyautogui.click(step.get_locations()[0])
```

### Pilot: Automation Runner
Execute and manage workflows:
```python
pilot = Pilot("automation.ipynb")
pilot.run_workbook()  # Full workflow
pilot.run_workbook(firstStep=3)  # Resume from step 3
```

### Binoculars: Visual Debugger
Monitor and troubleshoot automations remotely:
```python
viewer = Binoculars()
viewer.start_monitoring("_automation")  # Live monitoring
viewer.debug_screenshot("failed_step.png")  # Debug mode
```

### AL: Air-Gapped AI Assistant
Integrate local LLM-based decision making:
```python
from pyperiscope import AL
ai = AL(interface="ollama", model="llama3")  # Runs on automation server
selections = ["fruit", "vegetables", "python script"]
response = ai.ask(f"Please select from options: {selections}\nContext: {inputtext}")
```

## Workflow Development

1. **Setup**
   - Connect to automation server's Jupyter Lab
   - Create new automation notebook
   - Document workflow requirements in markdown

2. **Development**
   - Use Scraper on automation server to capture elements
   - Create step definitions in notebook cells
   - Test elements with running the cells in any order necessary
   - Implement error handling and recovery logic

3. **Testing**
   - Run complete workflow with Pilot
   - Monitor execution with Binoculars
   - Debug and adjust confidence levels as needed
   - Save working configurations

## Best Practices

1. **Environment Setup**
   - Ensure automation server has required screen access
   - Configure Jupyter Lab for remote access
   - Set up local LLM if using AI assistance
   - Verify all dependencies on automation server

2. **Development**
   - Document each step thoroughly in markdown
   - Use Binoculars for real-time visual feedback
   - Implement appropriate error handling
   - Test AI decisions with sample scenarios

3. **Maintenance**
   - Monitor execution with Binoculars
   - Maintain backup of working configurations
   - Update element selections when UI changes
   - Document known failure scenarios and solutions

## Architecture Benefits

1. **Air-Gapped Ready**: Fully functional in secure environments
2. **Remote-First**: Designed for remote development and monitoring
3. **State Management**: Built-in error recovery and state tracking
4. **Modular Design**: Components work together seamlessly
5. **Local AI**: No external API dependencies for decision making