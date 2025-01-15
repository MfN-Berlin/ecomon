import os
from jinja2 import Environment, FileSystemLoader
import argparse

def generate_config(prefix, year, model, template, output_folder):
    context = {
        'prefix': prefix,
        'year': year,
        'model': model
    }
    output = template.render(context)
    
    # Create a subfolder for the model within the output folder
    model_output_folder = os.path.join(output_folder, model)
    if not os.path.exists(model_output_folder):
        os.makedirs(model_output_folder)
    
    output_filename = os.path.join(model_output_folder, f"config-{prefix}-{year}.yaml")
    with open(output_filename, 'w') as f:
        f.write(output)
    print(f"YAML file '{output_filename}' generated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Generate YAML configuration files.")
    parser.add_argument('--prefix', type=str, help='The prefix to use in the configuration.')
    parser.add_argument('--year', type=str, help='The year to use in the configuration.')
    parser.add_argument('--model', type=str, choices=['birdid', 'birdnet'], required=True, help='The model to use in the configuration (birdid or birdnet).')
    parser.add_argument('--folder', type=str, help='Path to a folder. Generate configs for each subfolder as prefix.')
    parser.add_argument('--output', type=str, required=True, help='Output folder for generated configuration files.')
    parser.add_argument('--filter', type=str, help='Filter subfolders by this substring.')

    args = parser.parse_args()

    # Ensure the output folder exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # Determine the template file based on the model
    template_file = f'./config-templates/{args.model}_template.yaml'

    # Load the template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)

    if args.folder:
        # Generate configs for each subfolder
        for subfolder in os.listdir(args.folder):
            subfolder_path = os.path.join(args.folder, subfolder)
            # Ignore hidden folders and apply filter if specified
            if os.path.isdir(subfolder_path) and not subfolder.startswith('.'):
                if args.filter and args.filter not in subfolder:
                    continue
                generate_config(subfolder, args.year, args.model, template, args.output)
    else:
        # Generate a single config
        if not args.prefix or not args.year:
            parser.error("The --prefix and --year arguments are required unless --folder is specified.")
        generate_config(args.prefix, args.year, args.model, template, args.output)

if __name__ == "__main__":
    main()