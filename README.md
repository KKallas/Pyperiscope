**Pypersicope**
================

A Lightweight Web-Based Automation Tool
-----------------------------------------

### Overview

Pypersicope is an open-source, web-based automation tool that enables users to create and run complex software automation workflows using simple, human-readable instructions. The tool utilizes Python, pyautogui, and a custom-designed web interface to provide an intuitive and powerful automation platform.

### Features

* Lightweight web server with a single, human-readable page for creating and running automation workflows
* Full-resolution screenshot display and text box (for Python code) for easy step-by-step instructions
* Stack of steps on the left side allows for easy navigation and modification of the workflow
* Supports point-and-click, wait-for-image, time-based, or event-based automation steps
* All interaction occurs through GET and POST endpoints, making it easily integrable with Large Language Models (LLMs) like LLaMA 3
* Ability to save and load workflows as zipped folders containing a single Python file and images

### Design Philosophy

Pypersicope is designed to be an ultra-simple automation interface that can be used by humans from cell phones or other devices. The tool aims to provide a reliable and fault-tolerant workflow recording mechanism, allowing users to pick up where they left off in case of any errors or interruptions.

### Target Audience

* Developers and designers who need to automate complex software workflows
* Students and researchers who require a simple, easy-to-use automation platform for educational or research purposes
* Professionals who need to streamline repetitive tasks and improve productivity

### Technical Requirements

* Python 3.x (recommended)
* pyautogui library
* Docker (optional) with OpenWebGUI (for running the tool on Unreal 5 Editor project)

### LLaMA Integration

Pypersicope is designed to work seamlessly with LLaMA 3 and other LLMs. Users can choose their preferred LLM and integrate it with Pypersicope to create a powerful automation workflow.

### Roadmap

* 1st release
* Image detection
* Ollama integeration for text descriptions
* YOLO for abstract detection
* Object movement and out view presistance

### Contributing

We welcome contributions, suggestions, and ideas from the community! If you'd like to contribute to Pypersicope, please feel free to reach out or open an issue on GitHub.

Thank you for considering Pypersicope! We hope this tool will help simplify your automation workflow and improve productivity.
