import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from unidecode import unidecode
from tkinter import filedialog
import shutil
import pandas as pd
import os

# Set the working directory to the directory of your script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

os.environ["OPENAI_API_KEY"] = ''

from llama_hub.file.base import SimpleDirectoryReader
from llama_index import GPTVectorStoreIndex

index = None

def analyze_documents():
    loader = SimpleDirectoryReader('./data/documents', recursive=True, exclude_hidden=True)
    documents = loader.load_data()
    global index
    index = GPTVectorStoreIndex.from_documents(documents)
    messagebox.showinfo("Análisis", "Los documentos cargados fueron analizados")


def load_and_save_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    
    if file_path:
        # Get the program's location
        program_location = os.path.dirname(os.path.abspath(__file__))
        destination_folder = os.path.join(program_location, "data/documents")
        
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        else:
            # Clear the contents of the data folder
            for filename in os.listdir(destination_folder):
                file_path_to_remove = os.path.join(destination_folder, filename)
                if os.path.isfile(file_path_to_remove):
                    os.remove(file_path_to_remove)
        
        file_name = os.path.basename(file_path)
        destination_path = os.path.join(destination_folder, file_name)
        
        try:
            shutil.copy(file_path, destination_path)
            messagebox.showinfo("Éxito", f"Archivo '{file_name}' guardado para analizar")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")


def preguntar_button_click():
    pregunta = pregunta_var.get()
    
    if pregunta:
        query_engine = index.as_query_engine()
        response = query_engine.query(pregunta)
        
        # You can do something with the 'response' here, like displaying it in a popup
        show_custom_info("Respuesta de ChatGPT", "Respuesta:", response, 800, 400)
    else:
        messagebox.showinfo("Aviso", "Ingrese una pregunta antes de preguntar.")



def show_custom_info(title, result, message, width, height):
    info_dialog = tk.Toplevel()
    info_dialog.title(title)
    
    # Set the size of the custom window
    info_dialog.geometry(f"{width}x{height}")
    
    title_label = tk.Label(info_dialog, text=result, font=("Helvetica", 12, "bold"))
    title_label.pack(padx=20, pady=10)
    
    text_widget = tk.Text(info_dialog, font=("Helvetica", 10), wrap="word")  # Use Text widget for text display
    text_widget.pack(fill="both", expand=True)
    text_widget.insert("1.0", message)  # Insert the message into the Text widget
    
    ok_button = ttk.Button(info_dialog, text="OK", command=info_dialog.destroy)
    ok_button.pack(side="left", padx=10)

    predatory_button = ttk.Button(info_dialog, text="Análisis de Revistas Depredadoras", command=search_predatory)
    predatory_button.pack(side="left", padx=50)

def show_custom_info_predatory(title, result, message, width, height):
    info_dialog = tk.Toplevel()
    info_dialog.title(title)
    
    # Set the size of the custom window
    info_dialog.geometry(f"{width}x{height}")
    
    title_label = tk.Label(info_dialog, text=result, font=("Helvetica", 12, "bold"))
    title_label.pack(padx=20, pady=10)
    
    text_widget = tk.Text(info_dialog, font=("Helvetica", 10), wrap="word")  # Use Text widget for text display
    text_widget.pack(fill="both", expand=True)
    text_widget.insert("1.0", message)  # Insert the message into the Text widget
    
    ok_button = ttk.Button(info_dialog, text="OK", command=info_dialog.destroy)
    ok_button.pack(side="left", padx=10)

def search_predatory():
    search_name = name_var.get()
    predatory = pd.read_csv("data\databases\predatory.csv")
    data = predatory
    name = 'NAME'

    search_name = search_name.lower()  # Convert input to lowercase
    result = None
    # Use boolean indexing to filter rows where the value exactly matches the search_name in the specified column
    # Remove spaces and convert to ASCII characters without accents
    search_name_no_accents = unidecode(search_name.lower())
    match_rows = data[data[name].apply(unidecode).str.lower() == search_name_no_accents]

    # Check if any exact match rows were found
    if not match_rows.empty:
        # Retrieve information from the exact match rows
        title = str(match_rows[name].iloc[0])
        # Create the message string with the retrieved values
        result = (
            f"La fuente '{title}' se encuentra dentro de lista de publicaciones depredadoras. Tenga cuidado al publicar en ella. \n"
        )

    else:
        # No exact match found, perform partial matching
        # Remove spaces and convert to ASCII characters without accents
        search_name_no_spaces = unidecode(search_name.replace(" ", "")).lower()
        match_rows = data[data[name].str.replace(" ", "").apply(unidecode).str.lower().str.contains(search_name_no_spaces)]
        
        if not match_rows.empty:
            if len(match_rows) == 1:
                # Only one partial match found, retrieve information from it
                title = str(match_rows[name].iloc[0])
                # Create the message string with the retrieved values
                result = (
                f"La fuente '{title}' se encuentra dentro de lista de publicaciones depredadoras. Tenga cuidado al publicar en ella. \n"
                )
            else:
                result = (
                    f"Su revista no se encuentra en la lista de Predatory Reports."
                )
        else:
            result = (
                    f"Su revista no se encuentra en la lista de Predatory Reports."
                )    
    show_custom_info_predatory("Revistas depredadoras","Análisis de Revistas Depredadoras" , result, 600, 500)


def search_button_click():
    search_country = country_var.get()
    search_name = name_var.get()

    data_col = pd.read_csv("data\databases\publindex.csv")
    data_int = pd.read_csv("data\databases\scimagojr.csv")

    data = None  # Initialize data with a default value

    match search_country:
        case "Colombia":
            data = data_col
            name = 'NME_REVISTA_IN'
            rank = 'ID_CLAS_REV'
            institution = "Publindex"
        case "Internacional":
            data = data_int
            name = 'Title'
            rank = 'SJR Best Quartile'
            institution = "Scimago Journal & Country Rank"
        case _:
             messagebox.showinfo("Aviso", "Elija una opción válida.")

    search_name = search_name.lower()  # Convert input to lowercase
    result = None
            
    # Use boolean indexing to filter rows where the value exactly matches the search_name in the specified column
    # Remove spaces and convert to ASCII characters without accents
    search_name_no_accents = unidecode(search_name.lower())
    match_rows = data[data[name].apply(unidecode).str.lower() == search_name_no_accents]

    # Check if any exact match rows were found
    if not match_rows.empty:
        # Retrieve information from the exact match rows
        category = str(match_rows[rank].iloc[0])
        title = str(match_rows[name].iloc[0])
        # Create the message string with the retrieved values
        result = (
            f"La categoria de la fuente '{title}' es {category} según {institution}."
        )
    else:
        # No exact match found, perform partial matching
        # Remove spaces and convert to ASCII characters without accents
        search_name_no_spaces = unidecode(search_name.replace(" ", "")).lower()
        
        match_rows = data[data[name].str.replace(" ", "").apply(unidecode).str.lower().str.contains(search_name_no_spaces)]
        
        if not match_rows.empty:
            if len(match_rows) == 1:
                # Only one partial match found, retrieve information from it
                category = str(match_rows[rank].iloc[0])
                title = str(match_rows[name].iloc[0])
                # Create the message string with the retrieved values
                result = (
                    f"La categoria de la fuente '{title}' es {category} según {institution}."
                )
            else:
                result = (
                    f"Se encontraron {len(match_rows)} resultados parciales, sea más específico con su búsqueda."
                )
        else:
            result = (
                    f"No se encontraron resultados exactos ni parciales para su búsqueda."
                )

    match search_country:
        case "Colombia":
            text = """Publindex es un índice bibliográfico colombiano que categoriza y clasifica las revistas científicas publicadas en Colombia. La clasificación proporcionada por Publindex indica la calidad y el impacto de estas revistas dentro de la comunidad académica e investigadora del país. Las clasificaciones se basan en varios criterios, incluyendo la calidad editorial de la revista, el proceso de revisión por pares, la frecuencia de publicación y las métricas de citas. Existen diferentes niveles o categorías en la clasificación de Publindex, cada uno representando diferentes grados de calidad e impacto. Estas categorías incluyen:\n
            1. Publindex A1: Las revistas en esta categoría se consideran de la más alta calidad e impacto. Por lo general, tienen procesos rigurosos de revisión por pares, altos estándares editoriales y una influencia significativa en su campo.\n
            2. Publindex A2: Las revistas en esta categoría también tienen alta calidad e impacto, aunque podrían tener ligeramente menos citas o un proceso de revisión por pares un poco menos estricto en comparación con las revistas A1.\n
            3. Publindex B: Las revistas en esta categoría tienen buena calidad e impacto, pero podrían no cumplir con los criterios para las revistas A1 o A2. Aún se considera que son respetables y contribuyen de manera significativa a sus respectivos campos.\n
            4. Publindex C: Las revistas en esta categoría podrían tener un enfoque más regional o especializado y podrían no tener un impacto tan amplio. Sin embargo, siguen contribuyendo al discurso académico dentro de su nicho.\n
            5. Publindex D: Las revistas en esta categoría podrían ser más nuevas o tener un impacto más limitado. Aún se reconoce que son fuentes legítimas de información académica.\n
            Es importante tener en cuenta que las clasificaciones de Publindex son específicas de Colombia y se utilizan para evaluar la calidad de las revistas científicas colombianas. Los investigadores y académicos dentro de Colombia suelen referirse a estas clasificaciones al evaluar la credibilidad e impacto de las revistas para su trabajo.\n
            Las clasificaciones también pueden influir en decisiones relacionadas con la financiación y el reconocimiento académico. Sin embargo, fuera de Colombia, es posible que estas clasificaciones no tengan el mismo nivel de reconocimiento o influencia.\n"""
            show_custom_info("Resultado de la búsqueda",result,text,1000,600)
        case "Internacional":
            text = """El Scimago Journal & Country Rank (SJR) es un portal público que proporciona varias métricas e indicadores para revistas científicas y países. Una de las características del SJR es su sistema de clasificación por cuartiles, que se utiliza para categorizar revistas en función de su impacto dentro de sus respectivos campos.\n
            El sistema de clasificación por cuartiles divide las revistas en cuatro cuartiles, cada uno representando un segmento de la distribución de revistas dentro de una categoría temática específica. Estos cuartiles se calculan en función del indicador SJR, que tiene en cuenta no solo el número de citas recibidas por una revista, sino también el prestigio de las revistas que citan. Esto es lo que representa cada cuartil:\n
            1. Q1 (Top 25%): Las revistas en el primer cuartil se consideran las más prestigiosas e impactantes dentro de su categoría temática. Están entre el 25% superior de las revistas en términos de valores del indicador SJR. Estas revistas suelen tener un alto número de citas y se consideran influyentes en su campo.\n
            2. Q2 (Segundo 25%): Las revistas en el segundo cuartil aún son bien consideradas y tienen un impacto significativo, pero no son tan influyentes como las del primer cuartil. Se sitúan en el rango del 25 al 50% en términos de valores del indicador SJR.\n
            3. Q3 (Tercer 25%): Las revistas en el tercer cuartil se consideran que tienen un impacto moderado dentro de su categoría temática. Se sitúan en el rango del 50 al 75% en términos de valores del indicador SJR. Si bien estas revistas pueden no tener un impacto tan alto como las de los cuartiles superiores, siguen contribuyendo a la literatura académica.\n
            4. Q4 (Último 25%): Las revistas en el cuarto cuartil tienen el impacto más bajo dentro de su categoría temática. Se encuentran entre las revistas menos citadas y menos influyentes, situándose en el 25% inferior en términos de valores del indicador SJR.\n
            Es importante tener en cuenta que la clasificación por cuartiles es relativa a la categoría temática. Una revista que esté en el Q1 en una categoría temática podría estar en un cuartil diferente en otra categoría temática. Además, el sistema de clasificación por cuartiles es solo una forma de evaluar el impacto y el prestigio de una revista. Los investigadores suelen considerar varias métricas e indicadores al evaluar la importancia de una revista dentro de su campo.\n"""
            show_custom_info("Resultado de la búsqueda",result,text,1000,600)
        

# Create the main application window
app = tk.Tk()
app.title("Herramienta para Investigadores")

# Set the window size
app.geometry("600x600")  # Width x Height

# Add a title label
title_label = tk.Label(app, text="Herramienta para Investigadores", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)  # Add padding

# Add instructions
instructions = "Con este programa podrás consultar las bases de datos de revistas indexadas\n"
instructions += "Scimago para publicaciones internacionales y Publindex para publicaciones colombianas.\n"
instructions += "Podrás ver su ranking y qué significa su calificación.\n"
instructions += "Adicionalmente, podrás revisar si la revista se encuentra reportada por Predatory Reports.\n"
instructions += "Además, podrás cargar documentos PDF de tus artículos científicos y analizarlos usando ChatGPT.\n"
instructions += "Para poder hacerle preguntas sobre el contenido del documento cargado. \n"
instructions_label = tk.Label(app, text=instructions, justify="left")
instructions_label.pack()

instructions_label = tk.Label(app, text="")
instructions_label.pack()

# Add subtitle
subtitle_label = tk.Label(app, text="Buscador de revistas indexadas", font=("Helvetica", 12, "bold"))
subtitle_label.pack(pady=10)  # Add padding

# Create and place widgets
country_label = tk.Label(app, text="Seleccione el origen de su fuente:")
country_label.pack()
country_var = tk.StringVar()
country_selector = tk.OptionMenu(app, country_var, "Colombia", "Internacional")
country_selector.pack()

name_label = tk.Label(app, text="Ingrese el nombre de su fuente:")
name_label.pack()
name_var = tk.StringVar()
name_entry = tk.Entry(app, textvariable=name_var, width=40)  # Adjust width here
name_entry.pack()

search_button = tk.Button(app, text="Buscar", command=search_button_click)
search_button.pack()

# Add subtitle
subtitle_label = tk.Label(app, text="Análisis de textos por ChatGPT", font=("Helvetica", 12, "bold"))
subtitle_label.pack(pady=10)  # Add padding

load_pdf_label = tk.Label(app, text="Seleccione un archivo PDF para analizar:")
load_pdf_label.pack(pady=5)
load_pdf_button = tk.Button(app, text="Cargar PDF", command=load_and_save_pdf)
load_pdf_button.pack()

analyze_button = tk.Button(app, text="Analizar", command=analyze_documents)
analyze_button.pack(pady=5)

pregunta_label = tk.Label(app, text="Ingrese su pregunta:")
pregunta_label.pack()
pregunta_var = tk.StringVar()
pregunta_entry = tk.Entry(app, textvariable=pregunta_var, width=80)  # Adjust width here
pregunta_entry.pack()

preguntar_button = tk.Button(app, text="Preguntar", command=preguntar_button_click)
preguntar_button.pack()

app.mainloop()
