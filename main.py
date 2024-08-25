import markdown, os, sys, time, webbrowser, shutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def read(file):
    with open(file) as f:
        return f.read()
    
def clear_output_directory():
    output_dir = "out"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
header_template = read("templates/header.html")
footer_template = read("templates/footer.html")

def render(dirname, title):
    base_dir = os.path.join("data", dirname)
    entities = [x for x in os.listdir(base_dir) if x != 'index.md']
    entities.sort()
    links = {}
    
    for entity in entities:
        if not os.path.isfile(entity):
            try:
                os.mkdir(os.path.join("out", dirname, entity))
            except FileExistsError:
                pass
            sub_title = entity[6:]
            render(os.path.join(dirname, entity), sub_title)
            links[sub_title] = os.path.join(dirname, entity, "index.html")
        else:
            src = os.path.join(base_dir, entity)
            dst = os.path.join("data", dirname, entity)
            print(f"Copying {src} to {dst}")
            shutil.copyfile(src, dst)

    md_content = ""

    with open(os.path.join(base_dir, "index.md")) as file:
        md_content = file.read()

    html = markdown.markdown(md_content, extensions=['mdx_math'])

    final = header_template + html + footer_template

    final += """
        <h3>Contents</h3>
        <ul>
    """

    for title in links:
        link = links[title]
        final += f'<a href="{link}">{title}</a>'

    final += "</ul>"

    final += f"""
        <script>
            document.title = '{ title }';
        </script>
    """

    final += footer_template

    with open(os.path.join("out", dirname, "index.html"), "w+") as file:
        file.write(final)
        file.close()

class RerunHandler(FileSystemEventHandler):
    def __init__(self, script_name):
        self.script_name = script_name

    def on_modified(self, event):
        print(f"{self.script_name} or markdown file modified. Restarting...")
        os.execv(sys.executable, ['python'] + sys.argv)

print("Started. Reload browser to see changes")

if __name__ == "__main__":
    script_name = sys.argv[0]

    event_handler = RerunHandler(script_name)
    observer = Observer()
    observer.schedule(event_handler, path='data', recursive=True)
    observer.start()

    webbrowser.open(os.path.realpath("out/index.html"))
    
    try:
        while True:
            time.sleep(1)
            clear_output_directory()
            render("", "Open Source Book")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
else:
    clear_output_directory()
    render("", "Open Source Book")