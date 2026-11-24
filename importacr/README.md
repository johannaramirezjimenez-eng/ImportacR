# ImportaCR

Sistema de gestión de importaciones para Costa Rica. Calcula la obligación tributaria aduanera según el
*Instructivo de cálculo de la obligación tributaria* de la Dirección General de Aduanas (2023), clasifica
mercancías con la Lista de Costa Rica del CAFTA-DR y reúne en un solo expediente la ruta logística, los
permisos, los riesgos y el costo puesto en bodega.

Prototipo desarrollado como propuesta de investigación del curso Procesos de Importaciones,
Universidad San Marcos.

---

## Publicar la aplicación (sin instalar nada)

Todo se hace desde el navegador. Toma unos 20 minutos la primera vez.
Los nombres de algunos botones pueden variar un poco si GitHub o Streamlit actualizan sus páginas.

### Paso 1. Crear una cuenta en GitHub

1. Entre a **https://github.com** y haga clic en **Sign up**.
2. Use su correo, cree una contraseña y un nombre de usuario (por ejemplo, `johanna-ramirez`).
3. Confirme el correo con el código que le envían.

### Paso 2. Crear el repositorio (la carpeta donde vivirá el código)

1. Ya dentro de GitHub, haga clic en el botón **+** (arriba a la derecha) y luego en **New repository**.
2. En **Repository name** escriba `importacr`.
3. Deje marcada la opción **Public**.
4. **No** marque "Add a README file".
5. Haga clic en **Create repository**.

### Paso 3. Subir los archivos

1. Descomprima en su computadora el archivo `importacr.zip`. Obtendrá una carpeta `importacr`.
2. En la página del repositorio recién creado, haga clic en el enlace **uploading an existing file**.
3. Abra la carpeta `importacr` de su computadora, seleccione **todo su contenido**
   (los archivos `.py`, `requirements.txt`, `README.md` y la carpeta `data`) y arrástrelo a la ventana de GitHub.
4. Espere a que terminen de cargar y haga clic en **Commit changes**.
5. Revise que en el repositorio aparezcan: `app.py`, `motor.py`, `arancel.py`, `catalogo.py`, `casos.py`,
   `validacion.py`, `requirements.txt`, `README.md` y la carpeta `data` (con `cafta_cr.json` adentro).

### Paso 4. Agregar los colores de la aplicación

La carpeta `.streamlit` suele estar oculta en Windows y Mac, por eso se crea directamente en GitHub:

1. En el repositorio, haga clic en **Add file** → **Create new file**.
2. En el nombre del archivo escriba exactamente: `.streamlit/config.toml`
3. Pegue este contenido:

```toml
[theme]
base = "light"
primaryColor = "#1f7fb5"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f1f6fb"
textColor = "#10223a"
font = "sans serif"

[browser]
gatherUsageStats = false
```

4. Haga clic en **Commit changes** (dos veces, si se lo pide).

### Paso 5. Publicar en Streamlit Community Cloud

1. Entre a **https://share.streamlit.io** y elija **Continue with GitHub**. Autorice el acceso.
2. Haga clic en **Create app** y luego en **Deploy a public app from GitHub**.
3. Complete:
   - **Repository:** `su-usuario/importacr`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** escriba un nombre corto, por ejemplo `importacr` (si está ocupado, pruebe `importacr-cr`).
4. Haga clic en **Deploy**. La primera vez tarda dos o tres minutos.
5. Cuando cargue, copie el enlace del navegador (por ejemplo `https://importacr.streamlit.app`).
   **Ese es el enlace que se envía al profesor.** No necesita cuenta ni instalar nada.

### Cambios posteriores

Si edita un archivo en GitHub (ícono del lápiz → **Commit changes**), la aplicación se actualiza sola en uno o dos minutos.

### Si algo falla

- **"Error installing requirements"**: revise que `requirements.txt` esté en la raíz del repositorio, no dentro de otra carpeta.
- **"FileNotFoundError: data/cafta_cr.json"**: la carpeta `data` no se subió. Repita el paso 3 con esa carpeta.
- **La aplicación "se duerme"**: si nadie la usa por varios días, Streamlit la suspende. Al abrirla aparece un botón
  para reactivarla; tarda menos de un minuto. Conviene abrirla el día antes de la entrega.

---

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `app.py` | Interfaz: expedientes, liquidación, clasificación, logística, permisos, riesgos, costos, colaboración y fuentes |
| `motor.py` | Cálculo de la obligación tributaria (instructivo DGA 2023) y desgravación del CAFTA-DR (Anexo 3.3) |
| `arancel.py` | Búsqueda en la Lista de Costa Rica y reglas especiales de las Notas Generales |
| `catalogo.py` | Tipos de mercancía, países y tratados, aduanas, etapas, riesgos y referencias |
| `casos.py` | Expedientes de demostración y creación de expedientes nuevos |
| `validacion.py` | Pruebas del motor contra los ejemplos oficiales del instructivo |
| `data/cafta_cr.json` | 7 534 líneas de la Lista de Costa Rica (código SAC, descripción, tasa base y categoría) |

## Validación

El motor reproduce los ejemplos oficiales del instructivo de la DGA (2023): whisky (sección M) y ron con
trato preferencial (sección N). Las tarifas vigentes de cada inciso se confirman en el arancel integrado
del TICA: https://ticaconsultas.hacienda.go.cr/tica/hdbaranc.aspx

## Ejecutar en una computadora (opcional)

```bash
pip install -r requirements.txt
streamlit run app.py
```
