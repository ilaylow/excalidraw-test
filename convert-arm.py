import json5
import json
import os
import argparse
import re

ROLLOUT_SPEC_ID = "rolloutspec"
SERVICE_MODEL_ID = "servicemodel"
SCOPE_BINDING_ID = "scopebinding"
CONFIG_ID = "config"

ROLLOUT_SPEC_POS = (-10, 0)
SERVICE_MODEL_POS = (-230, 100)
SCOPE_BINDING_POS = (210, 100)
CONFIG_POS = (0, 100)

STANDARD_HEIGHT = 40
STANDARD_WIDTH = 200

PADDING_HEIGHT = 20

FONT_SIZE = 13

# Accept in argument for path of the rolloutspec
parser = argparse.ArgumentParser(description='Create relationship diagram from EV2 Rollout Spec File. (Must be Absolute File Path)')

parser.add_argument("--file", type=str, required=True, help='File path to the rollout spec file')

args = parser.parse_args()

# Validate that rollout spec file exists
rollout_spec_file_path = str(args.file).replace("\\", "/")

if not os.path.isfile(rollout_spec_file_path):
    print("Invalid file path or file does not exist")
    exit

# Parse rollout spec - and parse through elements
with open(rollout_spec_file_path, 'r') as file:
    rollout_spec_file_data = json5.load(file)

root_dir = rollout_spec_file_path.split("/")[:-2]
root_dir = "/".join(root_dir)

rollout_spec_filename = rollout_spec_file_path.split("/")[-1]
rollout_infra = rollout_spec_file_path.split("/")[-1].split(".")[1]

service_model_path = os.path.join(root_dir, rollout_spec_file_data['rolloutMetadata']['serviceModelPath']).replace("\\", "/")
service_model_filename = service_model_path.split("/")[-1]

scope_bindings_path = os.path.join(root_dir, rollout_spec_file_data['rolloutMetadata']['scopeBindingsPath']).replace("\\", "/")
scope_bindings_filename = scope_bindings_path.split("/")[-1]

config_path = os.path.join(root_dir, rollout_spec_file_data['rolloutMetadata']['configuration']['serviceScope']['specPath']).replace("$rolloutInfra()", rollout_infra).replace("\\", "/")
config_filename = config_path.split("/")[-1]

# Validate that all mentioned files in first layer exist
service_model_exist = "✅" if os.path.isfile(service_model_path) else "❌"
print(f"Service Model exists: {service_model_exist}")

scope_bindings_exist = "✅" if os.path.isfile(scope_bindings_path) else "❌"
print(f"Scope Bindings exists: {scope_bindings_exist}")

config_exist = "✅" if os.path.isfile(config_path) else "❌"
print(f"Config exists: {config_exist}")

# Build first 4 entities
draw_elements = [
    {  
        "type": "arrow",
        "x": -25,
        "y": -103,
        "width": 30,
        "height": 0,
    },
    {  
        "type": "arrow",
        "x": -25,
        "y": -63,
        "width": 30,
        "height": 0,
        "strokeColor": "#e82e47",
    },
    {
        "type": "text",
        "x": 20,
        "y": -110,
        "fontSize": 13,
        "text": "indicates file reference"
    },
    {
        "type": "text",
        "x": 20,
        "y": -70,
        "fontSize": 13,
        "text": "indicates variable reference within file"
    },
    {   # Rollout Spec
        "type": "rectangle",
        "x": ROLLOUT_SPEC_POS[0],
        "y": ROLLOUT_SPEC_POS[1],
        "height": STANDARD_HEIGHT,
        "width": STANDARD_WIDTH,
        "roundness": {
        "type": 3
        },
        "id": ROLLOUT_SPEC_ID,
        "backgroundColor": "#a5d8ff",
        "label": {
            "text": rollout_spec_filename,
            "fontSize": FONT_SIZE,
        },  
    },
    {   # Service Model
        "type": "rectangle",
        "x": SERVICE_MODEL_POS[0],
        "y": SERVICE_MODEL_POS[1],
        "height": STANDARD_HEIGHT,
        "width": STANDARD_WIDTH,
        "roundness": {
        "type": 3
        },
        "id": SERVICE_MODEL_ID,
        "backgroundColor": "#c778f5",
        "label": {
            "text": service_model_filename,
            "fontSize": FONT_SIZE,
        },  
    },
    {   # Config
        "type": "rectangle",
        "x": CONFIG_POS[0],
        "y": CONFIG_POS[1],
        "height": 40,
        "width": 180,
        "roundness": {
        "type": 3
        },
        "id": CONFIG_ID,
        "backgroundColor": "#f587e8",
        "label": {
            "text": config_filename,
            "fontSize": FONT_SIZE,
        },  
    },
    {   # Scope Bindings
        "type": "rectangle",
        "x": SCOPE_BINDING_POS[0],
        "y": SCOPE_BINDING_POS[1],
        "height": 40,
        "width": 160,
        "roundness": {
        "type": 3
        },
        "id": SCOPE_BINDING_ID,
        "backgroundColor": "#fff75e",
        "label": {
            "text": scope_bindings_filename,
            "fontSize": FONT_SIZE,
        },  
    }, 
    {   # Rollout Spec to Config
        "type": "arrow",
        "x": 90,
        "y": 40,
        "width": 1,
        "height": 60
    },
    {   # Rollout Spec to Service Model
        "type": "arrow",
        "x": 90,
        "y": 40,
        "width": -220,
        "height": 60
    },
    {   # Rollout Spec to Scope Bindings
        "type": "arrow",
        "x": 90,
        "y": 40,
        "width": 220,
        "height": 60
    },
    {   # Service Model to Config
        "type": "arrow",
        "x": 0,
        "y": 120,
        "width": -30,
        "height": 0,
        "strokeColor": "#e82e47",
        "startArrowhead": "arrow",
        "endArrowhead": "null",
    },
    {   # Scope Binding to Config
        "type": "arrow",
        "x": 180,
        "y": 120,
        "width": 30,
        "height": 0,
        "strokeColor": "#e82e47",
        "startArrowhead": "arrow",
        "endArrowhead": "null",
    }
]

# Find all links in service model
with open (service_model_path, "r") as f:
    service_model_file_data = json5.load(f)

service_groups = service_model_file_data["serviceResourceGroupDefinitions"]
parameters_files = []
templates_files = []
rollout_params_files = []

for service_group in service_groups:
    service_resources = service_group["serviceResourceDefinitions"]
    for service_resource in service_resources:
        composed_of = service_resource["composedOf"]
        if "arm" in composed_of:
            # Assume always well formed (templatePath and parametersPath is present)
            templates_files.append(composed_of["arm"]["templatePath"])
            parameters_files.append(composed_of["arm"]["parametersPath"])
        elif "extension" in composed_of:
            rollout_params_files.append(composed_of["extension"]["rolloutParametersPath"])

# Iterate through parameters and template files and link

# Encapsulating Box For Templates
draw_elements.append(
    {
        "type": "rectangle",
        "x": SERVICE_MODEL_POS[0] - 20,
        "y": SERVICE_MODEL_POS[1] + 130,
        "height": (len(templates_files) * (STANDARD_HEIGHT + PADDING_HEIGHT) + PADDING_HEIGHT),
        "width": STANDARD_WIDTH + 40,
        "roundness": {
            "type": 3
        },
        "backgroundColor": "#d0d6d6",
    }
)

# Encapsulating Box For Parameters
draw_elements.append(
    {
        "type": "rectangle",
        "x": SERVICE_MODEL_POS[0] + 280,
        "y": SERVICE_MODEL_POS[1] + 130,
        "height": (len(templates_files) * (STANDARD_HEIGHT + PADDING_HEIGHT) + PADDING_HEIGHT),
        "width": STANDARD_WIDTH + 40,
        "roundness": {
            "type": 3
        },
        "backgroundColor": "#d0d6d6",
    }
)

# Draw template boxes
for i in range(len(templates_files)):
    template_filename = templates_files[i].split("\\")[-1]
    template_draw_element = { 
        "type": "rectangle",
        "x": SERVICE_MODEL_POS[0],
        "y": SERVICE_MODEL_POS[1] + 130 + ((i) * (STANDARD_HEIGHT + PADDING_HEIGHT)) + PADDING_HEIGHT,
        "height": 30,
        "width": 200,
        "roundness": {
        "type": 3
        },
        "id": SERVICE_MODEL_ID,
        "backgroundColor": "#64ede0",
        "label": {
            "text": template_filename,
            "fontSize": FONT_SIZE,
        },  
    }

    parameter_filename = parameters_files[i].split("\\")[-1]
    parameter_draw_element = { 
        "type": "rectangle",
        "x": SERVICE_MODEL_POS[0] + 300,
        "y": SERVICE_MODEL_POS[1] + 130 + ((i) * (STANDARD_HEIGHT + PADDING_HEIGHT)) + PADDING_HEIGHT,
        "height": 30,
        "width": 200,
        "roundness": {
        "type": 3
        },
        "id": SERVICE_MODEL_ID,
        "backgroundColor": "#64ede0",
        "label": {
            "text": parameter_filename,
            "fontSize": FONT_SIZE,
        },  
    }

    connecting_arrow_element = {
        "type": "line",
        "x": SERVICE_MODEL_POS[0] + 200,
        "y": SERVICE_MODEL_POS[1] + 130 + ((i) * (STANDARD_HEIGHT + PADDING_HEIGHT)) + PADDING_HEIGHT + 20,
        "width": "10"
    }

    draw_elements.append(template_draw_element)
    draw_elements.append(parameter_draw_element)
    draw_elements.append(connecting_arrow_element)

# Draw arrow from Service Model to Templates
draw_elements.append(
    {   # Rollout Spec to Service Model
        "type": "arrow",
        "x": SERVICE_MODEL_POS[0] + (STANDARD_WIDTH // 2),
        "y": SERVICE_MODEL_POS[1] + STANDARD_HEIGHT,
        "width": -1,
        "height": 90,
    },
)

# Draw arrow from Parameters to Scope Bindings
draw_elements.append(
    {   # Rollout Spec to Service Model
        "type": "arrow",
        "x": SERVICE_MODEL_POS[0] + 400,
        "y": SERVICE_MODEL_POS[1] + 130,
        "width": 120,
        "height": -90,
        "strokeColor": "#e82e47",
    },
)

# Draw rollout params elements
if len(rollout_params_files):
    for i in range(len(rollout_params_files)):
        rollout_param = rollout_params_files[i].split("\\")[-1]
        
        # This needs to be fixed
        draw_elements.append(
            {
                "type": "rectangle",
                "x": SERVICE_MODEL_POS[0] - 300,
                "y": SERVICE_MODEL_POS[1],
                "height": STANDARD_HEIGHT,
                "width": STANDARD_WIDTH,
                "roundness": {
                    "type": 3
                },
                "id": SERVICE_MODEL_ID,
                "backgroundColor": "#6de89a",
                "label": {
                    "text": rollout_param,
                    "fontSize": FONT_SIZE,
                },  
            }
        )

        # This needs to be fixed
        draw_elements.append(
            {
                "type": "arrow",
                "x": SERVICE_MODEL_POS[0],
                "y": SERVICE_MODEL_POS[1] + 20,
                "width": -100,
            }
        )

# Draw arrow from rollout params to scope bindings
draw_elements.append(
    {
        "type": "arrow",
        "x": SERVICE_MODEL_POS[0] - 100,
        "y": SERVICE_MODEL_POS[1] + 20,
        "points": [
            [
                0,
                0
            ],
            [
                300,
                80,
            ],
            [
                575,
                20,
            ]
        ],
        "strokeColor": "#e82e47",
    }
)

# Load in config file 
with open(config_path, "r") as f:
    config_file_data = json5.load(f)
    config_data = config_file_data["settings"]

# Load in scope bindings file - get mapping to config params
with open(scope_bindings_path, "r") as f:
    scope_bindings_file_data = json5.load(f)
    scope_bindings = scope_bindings_file_data["scopeBindings"]
    for scope_binding in scope_bindings:
        bindings = scope_binding["bindings"]
        for binding in bindings:
            find = binding["find"]
            config_expression = binding["replaceWith"]
            match = re.search(r"\$config\((.*?)\)", config_expression)
            if not config_expression:
                print(f"Could not find value for {find}")
                continue
            if not match:
                print(f"Could not find value for {find}")
                continue
            config_expression = match.group(1)
            config_expression_list = config_expression.split(".")
            config_value = config_data
            use_fallback = False
            for val_step in config_expression_list:
                if val_step not in config_value:
                    use_fallback = True
                    break
                config_value = config_value[val_step]
            
            if use_fallback:
                if "fallback" not in binding:
                    print(f"Could not find value for {find}")
                    continue
                else:
                    config_value = binding["fallback"]["to"]
            
            print(f"{find}:{config_expression}:{config_value}")
                    

# Create boxes for each param file
for param_file in parameters_files:
    
    # Load in file data 
    param_file_path = os.path.join(root_dir, param_file).replace("\\", "/")
    with open(param_file_path, "r") as f:
        param_file_data = json.load(f)
        params = param_file_data["parameters"]


# Export elements to be loaded into excalidraw
with open('./public/excalidraw_elements.json', 'w') as f:
    json.dump(draw_elements, f)
    print("\nWrote elements to file public/excalidraw_elements.json")


