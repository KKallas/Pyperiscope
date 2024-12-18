**Pypersicope**
================
![image](https://github.com/user-attachments/assets/227ad299-eeef-4063-bcbb-c0e0d5be3cb7)



A Lightweight Visual Automation System
-----------------------------------------

### Overview

This Visual Automation System, a digital doppelgänger of human action, operates within the confines of Jupyter Lab. It creates and executes automated workflows based on the recognition of screen elements, much like an artificial eye scanning a landscape.
Smaple workflow automation built with PyPeriscope, run a calculator and add 5 and 11 [sample workflow](https://github.com/KKallas/Pyperiscope/blob/main/tests/test%20-%20calc%20win.ipynb)

### Features

* Grab a portion of the screen like a snip tool
* Store the snips with logic in each automation workbook as base64 string
* Run workflow by running the workbook
* Supports point-and-click, wait-for-image, time-based, or event-based automation steps

### Design Philosophy

Pypersicope is designed to be an ultra-simple automation interface that can be used by humans from cell phones or other devices. The tool aims to provide a reliable and fault-tolerant workflow recording mechanism, allowing users to pick up where they left off in case of any errors or interruptions.
The library is developed for [**Simple Software Dogmas**](https://github.com/KKallas/SimpleSoftwareDogmas)

### Target Audience

The Scope class is designed for capturing and processing screenshots using Python's pyautogui and image manipulation libraries. It allows users to capture a portion of their screen, define specific areas of interest, and save or load these areas as base64-encoded images. Below is an overview of how to use the class.

### LLaMA Integration

Pypersicope is designed to work seamlessly with LLaMA 3 and other LLMs. Users can choose their preferred LLM and integrate it with Pypersicope to create a powerful automation workflow.

### Roadmap

* 1st release
* Image detection
* Ollama integeration for text descriptions
* Launch control and error handeling

### Contributing

We welcome contributions, suggestions, and ideas from the community! If you'd like to contribute to Pypersicope, please feel free to reach out or open an issue on GitHub.

Thank you for considering Pypersicope! We hope this tool will help simplify your automation workflow and improve productivity.
