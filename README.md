# Bolão Support — Ranking em tempo real (Firebase + GitHub Actions)

## Checklist de configuração (feito por você, uma vez)

### 1. Criar o projeto Firebase
1. Acesse https://console.firebase.google.com/ e clique em **Adicionar projeto**.
2. Dê um nome (ex.: `bolao-ranking`) e finalize a criação (não precisa de Google Analytics).

### 2. Ativar Firestore
1. No menu lateral, vá em **Compilação > Firestore Database > Criar banco de dados**.
2. Escolha **modo de produção** e a região mais próxima (ex.: `southamerica-east1`).

### 3. Ativar login com Google
1. Menu lateral **Compilação > Authentication > Get started**.
2. Aba **Sign-in method** > ative o provedor **Google**.

### 4. Registrar o app Web (para pegar a config pública)
1. Na tela inicial do projeto, clique no ícone **</>** (Web app).
2. Dê um apelido (ex.: `bolao-web`) e registre.
3. Copie o objeto `firebaseConfig` mostrado — vai ter `apiKey`, `authDomain`, `projectId`, etc.
4. Cole esses valores no arquivo `index.html`, substituindo os placeholders `SEU_API_KEY`, `SEU_PROJECT_ID`, etc.

### 5. Gerar a chave da conta de serviço (para o GitHub Actions escrever no Firestore)
1. **Configurações do projeto** (ícone de engrenagem) **> Contas de serviço**.
2. Clique em **Gerar nova chave privada** — baixa um arquivo `.json`.
3. **Não** cole esse arquivo aqui no chat nem o commite no repositório. Guarde-o localmente.

### 6. Criar a lista de e-mails autorizados no Firestore
1. Em **Firestore Database > Dados**, crie manualmente:
   - Coleção: `config`
   - Documento com ID: `access`
   - Campo: `allowedEmails` (tipo **array**), com os e-mails do Google que podem entrar (o seu e os dos participantes que você autorizar).

### 7. Criar o repositório no GitHub
1. Crie um repositório novo (pode ser público — os dados sensíveis ficam no Firestore, não no repo).
2. Suba o conteúdo desta pasta (`bolao-ranking-web`) para ele.

### 8. Adicionar o secret no GitHub
1. No repositório: **Settings > Secrets and variables > Actions > New repository secret**.
2. Nome: `FIREBASE_SERVICE_ACCOUNT`
3. Valor: cole o **conteúdo inteiro** do arquivo `.json` baixado no passo 5.

### 9. Popular o histórico já coletado (uma vez só)
No seu PC, com Python e `firebase-admin` instalados:
```
cd scripts
set GOOGLE_APPLICATION_CREDENTIALS=C:\caminho\para\service-account.json
python seed_history.py
```

### 10. Publicar no Firebase Hosting
```
npm install -g firebase-tools
firebase login
firebase deploy --only hosting,firestore:rules
```
(edite antes o `.firebaserc`, trocando `SEU_PROJECT_ID_AQUI` pelo ID real do seu projeto)

### 11. Ativar o workflow do GitHub Actions
Ele já dispara sozinho a cada 15 minutos (`.github/workflows/update.yml`). Pode rodar manualmente uma vez pela aba **Actions > Atualizar ranking do bolão > Run workflow** para testar.

---

Depois desses passos, o site fica acessível pela URL que o Firebase Hosting fornecer (algo como `https://SEU_PROJECT_ID.web.app`), pedindo login Google e mostrando dados só para quem estiver na lista `allowedEmails`.
