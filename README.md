# Smarapd • Gerenciador de Chamados

Aplicação web simples (Flask + SQLite) que substitui a planilha de chamados de implantação:
número, título, status e data de conclusão. Tem login, filtro por status e exportação CSV.

## Rodar no seu computador (Python 3.15)
```bash
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5000  (usuário: admin / senha: smarapd123)
pytest                 # roda os testes
```

## Publicar na nuvem (Render.com – PaaS, o caminho mais simples)
1. Crie um repositório no GitHub e envie estes arquivos (`git init`, `git add .`, `git commit`, `git push`).
2. Em render.com → **New → Web Service** → conecte o repositório.
3. Configure:
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Health Check Path: `/health`
4. Em **Environment**, crie as variáveis: `PYTHON_VERSION` (use `3.15` ou a versão 3.15.x mais recente que o Render aceitar; se ele recusar, use `3.13`), `SECRET_KEY` (texto aleatório longo), `APP_USER`, `APP_PASSWORD`.
5. (Opcional, para os dados não se perderem a cada deploy) adicione um **Disk** montado em `/data` e crie a variável `DB_PATH=/data/chamados.db`. Em plano gratuito sem disco, o banco é zerado a cada novo deploy (ok para demonstração).
6. Cada `git push` na branch `main` faz o deploy automático (CD), e o GitHub Actions roda os testes (CI).

Alternativas equivalentes: Azure App Service, Google Cloud Run ou AWS Elastic Beanstalk (o `Dockerfile` já está pronto).

## Como isso atende ao PI
| Exigência do PI | Onde está |
|---|---|
| Aplicação web funcional hospedada na nuvem | App no Render (PaaS) |
| Deploy | Deploy automático a cada push (GitHub → Render) |
| Autenticação e permissões | Tela de login; rotas protegidas; credenciais em variáveis de ambiente |
| Segurança | HTTPS automático do Render, segredos fora do código |
| Domínio | Render → Settings → Custom Domains (ou use o domínio `.onrender.com`) |
| Escalabilidade | Render → Scaling (mais instâncias / autoscaling em plano pago); `Dockerfile` permite migrar para IaaS/containers |
| Monitoramento | `/health` + Health Checks, Logs e Metrics do Render; opcional UptimeRobot |
| Qualidade: testes | `test_app.py` (7 testes automatizados com pytest) |
| Qualidade: CI/CD | `.github/workflows/ci.yml` |
| Manutenibilidade | Código em um único arquivo, pequeno e organizado |

## Roteiro do vídeo (10–15 min)
1. Apresentar a Smarapd e o problema (planilha) – 1 min
2. Painel do provedor de nuvem: serviço criado, variáveis, logs, métricas, health check – 3 min
3. Aplicação funcionando: login, cadastrar, mudar status, filtrar, exportar CSV – 3 min
4. Código no GitHub, testes e pipeline do Actions passando – 3 min
5. Fazer um `git push` e mostrar o deploy automático – 2 min
6. ODS escolhido e conclusão – 1 min
