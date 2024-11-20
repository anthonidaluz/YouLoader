# Importação de módulos necessários
from flask import Flask, render_template, request, redirect, url_for, flash  # Flask para construir a aplicação web e gerenciar requisições HTTP
import yt_dlp  # type: ignore # Biblioteca para manipular vídeos e informações do YouTube
import os  # Para manipulação de operações relacionadas ao sistema operacional

# Inicializa o aplicativo Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Define uma chave secreta para gerenciar sessões e mensagens flash

# Rota principal para exibir e processar o formulário de entrada
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # Verifica se o método da requisição é POST
        url = request.form.get('url')  # Obtém a URL enviada pelo formulário
        if not url:  # Valida se a URL foi fornecida
            flash('Por favor, insira uma URL válida.', 'error')  # Exibe mensagem de erro
            return redirect(url_for('index'))  # Redireciona para a página inicial

        try:
            # Configuração para obter informações do vídeo
            ydl_opts = {'format': 'best'}  # Seleciona o melhor formato disponível
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)  # Extrai informações sem realizar o download

            # Filtra opções de qualidade de vídeo acima de 720p
            quality_options = [
                {'format_id': stream['format_id'], 'resolution': stream.get('resolution', 'N/A')}
                for stream in info['formats']
                if stream.get('height') and int(stream['height']) >= 720 and stream.get('vcodec') != 'none'
            ]

            if not quality_options:  # Caso nenhuma qualidade seja encontrada
                flash('Nenhuma qualidade disponível acima de 720p encontrada.', 'error')  # Exibe mensagem de erro
                return redirect(url_for('index'))

            # Renderiza a página inicial com as opções de qualidade e a URL fornecida
            return render_template('index.html', quality_options=quality_options, url=url)

        except Exception as e:  # Trata possíveis erros ao obter informações do vídeo
            flash(f'Ocorreu um erro ao obter as qualidades: {str(e)}', 'error')  # Exibe mensagem de erro
            return redirect(url_for('index'))

    # Renderiza a página inicial no caso de requisição GET
    return render_template('index.html')

# Rota para realizar o download do vídeo selecionado
@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')  # Obtém a URL do vídeo
    format_id = request.form.get('quality')  # Obtém o formato de qualidade selecionado

    if not url or not format_id:  # Valida se a URL e a qualidade foram especificadas
        flash('URL ou qualidade não especificada.', 'error')  # Exibe mensagem de erro
        return redirect(url_for('index'))  # Redireciona para a página inicial

    try:
        # Configuração para download do vídeo
        ydl_opts = {
            'format': format_id,  # Define o formato de qualidade selecionado
            'outtmpl': '%(title)s.%(ext)s',  # Define o nome do arquivo de saída
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])  # Realiza o download do vídeo

        flash('Download concluído!', 'success')  # Exibe mensagem de sucesso
    except Exception as e:  # Trata possíveis erros durante o download
        flash(f'Ocorreu um erro durante o download: {str(e)}', 'error')  # Exibe mensagem de erro

    return redirect(url_for('index'))  # Redireciona para a página inicial após o download

# Ponto de entrada da aplicação
if __name__ == '__main__':
    app.run(debug=True)  # Inicia o servidor em modo debug para facilitar o desenvolvimento
