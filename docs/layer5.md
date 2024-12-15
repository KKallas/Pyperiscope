# Scope String Generator

A utility method for the `Scope` class that helps generate new scope configurations from existing ones. This is particularly useful when:
- A recorded step doesn't work and you need to create a new step from the current position
- You want to create a new empty step while preserving parameters from an existing step

## Usage

### Basic Usage

```python
# Get string representation of current scope
current_step = Scope(mouse_offset=(10, 20))
print(current_step.generate_scope_string())
# Output: step = Scope(mouse_offset=(10, 20))
```

### Creating New Step from Current Position

If your recorded step isn't working, you can create a new one from your current position:

```python
# Create new step from current position
new_step = Scope()  # Empty step
current_step = Scope(area_size=(128, 128))  # Current position
print(new_step.generate_scope_string(current_step))
# Output: step = Scope(area_size=(128, 128))
```

### Parameters

The method takes one optional parameter:
- `step` (Scope, optional): Another Scope object to use as reference. If not provided, uses the current instance.

### Default Values

The method compares against these default values:
- `mouse_offset`: (0, 0)
- `area_offset`: (0, 0)
- `area_size`: (64, 64)
- `crop_size`: (640, 640)
- `cursor_size`: 32

Only non-default values will be included in the output string.

## Examples

```python
# Using current scope
step1 = Scope(mouse_offset=(10, 20), area_size=(128, 128))
print(step1.generate_scope_string())
# Output: step = Scope(mouse_offset=(10, 20), area_size=(128, 128))

# Using another scope as reference
step2 = Scope()  # Empty step
print(step2.generate_scope_string(step1))
# Output: step = Scope(mouse_offset=(10, 20), area_size=(128, 128))

# Using default values
step3 = Scope()
print(step3.generate_scope_string())
# Output: step = Scope()
```

[python](../src/pyperiscope/layer4.py)