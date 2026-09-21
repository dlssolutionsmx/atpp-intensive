# ATpp Intensive · Streamlit

El proyecto sirve ahora dos páginas dentro de la misma aplicación:

- `/` — panel principal basado en `index.html`.
- `/?page=intensive` — subpágina **ATpp Intensive**, que conserva la vista 2 original.

El botón **ATpp Intensive** del dashboard navega automáticamente a `?page=intensive`. Desde la subpágina, **Volver al dashboard** regresa a `?page=dashboard`.

## Ejecución local

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La aplicación carga las matrices Excel y los recursos del módulo Intensive únicamente cuando se accede a la subpágina correspondiente.

Esta etapa conserva la lógica interactiva de ATpp Intensive y utiliza el HTML adjunto como dashboard de entrada.
