import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PARTIALS_DIR = os.path.join(PROJECT_ROOT, 'static', 'partials')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'static', 'index.html')

# Define the order in which partials should be assembled
partials_order = {
    'head': '_head.html',
    'navbar': '_navbar.html',
    'tabs_nav': '_tabs_nav.html',
    'tab_chat': '_tab_chat.html',
    'tab_models': '_tab_models.html',
    'tab_foundry': '_tab_foundry.html',
    'tab_hf': '_tab_hf.html',
    'tab_llama': '_tab_llama.html',
    'tab_rag': '_tab_rag.html',
    'tab_settings': '_tab_settings.html',
    'tab_editor': '_tab_editor.html',
    'tab_examples': '_tab_examples.html',
    'tab_agent': '_tab_agent.html',
    'tab_mcp': '_tab_mcp.html',
    'tab_translation': '_tab_translation.html',
    'tab_logs': '_tab_logs.html',
    'tab_docs': '_tab_docs.html',
    'modal_llama_picker': '_modal_llama_picker.html',
    'modal_add_model': '_modal_add_model.html',
    'scripts': '_scripts.html',
}

def read_partial(name):
    path = os.path.join(PARTIALS_DIR, partials_order[name])
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def build_index_html():
    print(f"Building {OUTPUT_FILE} from partials...")
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
            outfile.write('''<!DOCTYPE html>
<html lang="ru">
''')
            outfile.write(read_partial('head'))
            outfile.write('''<body>
''')
            outfile.write(read_partial('navbar'))
            outfile.write('''    <div class="container mt-4">
''')
            outfile.write('''        <!-- Tabs Navigation -->
''')
            outfile.write(read_partial('tabs_nav'))
            outfile.write('''        <!-- Tab Content -->
''')
            outfile.write('''        <div class="tab-content" id="mainTabsContent">
''')
            
            # Dynamically add all tab panes
            for key in partials_order:
                if key.startswith('tab_'):
                    outfile.write(read_partial(key))

            outfile.write('''        </div>
''') # End tab-content
            outfile.write('''    </div>
''') # End container

            # Dynamically add all modals
            for key in partials_order:
                if key.startswith('modal_'):
                    outfile.write(read_partial(key))

            outfile.write(read_partial('scripts'))
            outfile.write('''</body>
</html>''')
        print(f"Successfully built {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error building index.html: {e}")
        raise

if __name__ == "__main__":
    build_index_html()
