Configure o script Python em @exportador_sei_isoleted.py para abrir o seu próprio navegador isolado e com uma pasta de usuário totalmente limpa. Algo como: 
``` python
# Em vez de se conectar ao Chrome existente, o script abre um novo Chrome limpo
# # Mas mantém a sua sessão salva em uma pasta local chamada "perfil_sei"
    browser_context = p.chromium.launch_persistent_context(

        user_data_dir=r"C:\SEI_Exportacoes\perfil_sei",

        headless=False, # Abre visualmente para você ver

        channel="chrome" # Usa o Chrome instalado, mas de forma isolada
    )

    page = browser_context.pages[0]

    page.goto("https://[URL_DO_SEI_DO_SEU_ORGAO]")
```
