import customtkinter as ctk
from tkinter import messagebox
import os
import time
import random
import datetime as dt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
from diagnostico import gerar_relatorio_ambiental, gerar_texto_diagnostico, gerar_diagnostico_complexidade, gerar_diagnostico_bigo
from log import executar_todos_algoritmos, medir_crescimento, verificar_corretude_algoritmos

from carregamento_data import (
    carregar_csv,
    filtrar_por_periodo,
    extrair_area_km,
    categorizar_faixas,
    agrupar_por_estado,
    agrupar_por_classe,
    agrupar_por_mes,
    EcoSortDataError,
)

CAMINHO_SEM_FILTRO = os.path.join(os.path.dirname(__file__), "..", "data", "Sem_Filtro.csv")
CAMINHO_COM_FILTRO = os.path.join(os.path.dirname(__file__), "..", "data", "Com_Filtro.csv")
LIMITE_AMOSTRA_BENCHMARK = 2000
# Muda a velocidade de execução do benchmark, mas não altera a análise final.

def _formatar_nome_categoria(nome):
    """Deixa nomes como CICATRIZ_DE_QUEIMADA legíveis: 'Cicatriz De Queimada'."""
    return str(nome).replace("_", " ").title()

# https://open.spotify.com/album/6DX4SASj4jxDSTPq9vz3RL?si=jLk-96wtS-iOSLnus1n7Aw&utm_source=whatsapp
def amostrar_para_benchmark(dados, limite=LIMITE_AMOSTRA_BENCHMARK):
    if len(dados) <= limite:
        return dados.copy()
    return random.sample(dados, limite)


class EcoSortApp:
    def __init__(self):
        self.modo_com_filtro = False  
        self.df_ativo = None
        self.dados_area = []
        self.tamanho_amostra = 0
        self.tempo_total = 0.0

    def carregar_base_ativa(self):
        caminho = CAMINHO_COM_FILTRO if self.modo_com_filtro else CAMINHO_SEM_FILTRO
        self.df_ativo = carregar_csv(caminho)

    def executar_analise(self, data_inicio=None, data_fim=None):
        inicio_cronometro = time.perf_counter() 

        df_filtrado = filtrar_por_periodo(self.df_ativo, data_inicio, data_fim)
        if df_filtrado.empty:
            raise EcoSortDataError("Nenhum registro encontrado para o período informado.")

        self.dados_area = extrair_area_km(df_filtrado)
        faixas = categorizar_faixas(self.dados_area)
        estado = agrupar_por_estado(df_filtrado)      
        classe = agrupar_por_classe(df_filtrado)       
        tempo_mensal = agrupar_por_mes(df_filtrado)  

        amostra = amostrar_para_benchmark(self.dados_area)
        self.tamanho_amostra = len(amostra)
        resultados = executar_todos_algoritmos(amostra)
        #
        texto_relatorio = gerar_relatorio_ambiental(self.dados_area, faixas)
        texto_diagnostico = gerar_texto_diagnostico(resultados)
        diag_inverso = gerar_diagnostico_complexidade(resultados["Inverso"])
        diag_aleatorio = gerar_diagnostico_complexidade(resultados["Aleatorio"])

        fim_cronometro = time.perf_counter()  
        self.tempo_total = fim_cronometro - inicio_cronometro

        return {
            "faixas": faixas,
            "estado": estado,                
            "classe": classe,                 
            "tempo_mensal": tempo_mensal,       
            "resultados": resultados,
            "relatorio": texto_relatorio,
            "diagnostico_texto": texto_diagnostico,
            "melhor": diag_inverso,
            "melhor_aleatorio": diag_aleatorio,
            "tempo_total": self.tempo_total,
        }


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")
# https://open.spotify.com/album/1DKgZeAYrjslAPZVMe6EFt?si=y9F0LWz5QJW1wYmVvEhXOA&utm_source=whatsapp
COR_SEM_FILTRO = "#2E7D32"
COR_COM_FILTRO = "#EF6C00"


class InterfaceEcoSort(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌲 EcoSort - Painel Autônomo de Inteligência Ambiental e Algorítmica")
        self.geometry("1280x900")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        self.motor = EcoSortApp()

        sucesso, mensagem = verificar_corretude_algoritmos()
        self.texto_corretude = (
            f"✅ Verificação de corretude: {mensagem}" if sucesso
            else f"❌ ERRO de corretude: {mensagem}"
        )
        if not sucesso:
            messagebox.showerror("Erro nos algoritmos", mensagem)

        self._montar_bloco1_topo()
        self._montar_bloco_proporcoes()      
        self._montar_bloco_tempo_mensal()
       
        self._montar_bloco3_relatorio()
        self._montar_bloco_bigo()
        self._montar_bloco_comparativo()            
        self._montar_bloco4_diagnostico()  
        self._montar_bloco_resumo_oficial()  
        self.after(100, self._carregar_e_executar)
        self.scroll_frame.bind_all("<MouseWheel>", self._forcar_redesenho, add="+")

    def _forcar_redesenho(self, event=None):
        self.scroll_frame._parent_canvas.update()
        self.update_idletasks()

    def _montar_bloco1_topo(self):
        frame = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        frame.pack(fill="x", padx=12, pady=12)
        frame.pack_propagate(False)     
        frame.configure(height=180) 

        titulo = ctk.CTkLabel(
            frame,
            text="EcoSort - Painel Autônomo de Inteligência Ambiental e Algorítmica",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        titulo.pack(anchor="w", padx=10, pady=(8, 12))
        # https://open.spotify.com/album/4T07AS6OKzpMp1EnM6zi1Q?si=UxFOV99fTY2SLACRCclO7w&utm_source=whatsapp
        linha_datas = ctk.CTkFrame(frame, fg_color="transparent")
        linha_datas.pack(fill="x", padx=10)

        ctk.CTkLabel(linha_datas, text="Data Início:").pack(side="left")
        self.entry_data_inicio = ctk.CTkEntry(linha_datas, placeholder_text="dd/mm/aaaa", width=120)
        self.entry_data_inicio.insert(0, "20/08/2021")
        self.entry_data_inicio.pack(side="left", padx=(4, 20))

        ctk.CTkLabel(linha_datas, text="Data Fim:").pack(side="left")
        self.entry_data_fim = ctk.CTkEntry(linha_datas, placeholder_text="dd/mm/aaaa", width=120)
        self.entry_data_fim.insert(0, "20/08/2025")
        self.entry_data_fim.pack(side="left", padx=(4, 20))

        ctk.CTkLabel(linha_datas, text="Atributo: areaMunKm", font=ctk.CTkFont(weight="bold")).pack(side="left")

        linha_botoes = ctk.CTkFrame(frame, fg_color="transparent")
        linha_botoes.pack(fill="x", padx=10, pady=10)

        self.botao_toggle = ctk.CTkButton(
            linha_botoes,
            text="🔄 MODO ATUAL: SEM FILTRO (Clique p/ alternar)",
            fg_color=COR_SEM_FILTRO,
            hover_color="#1B5E20",
            command=self._alternar_filtro,
        )
        self.botao_toggle.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.botao_executar = ctk.CTkButton(
            linha_botoes,
            text="🚀 EXECUTAR ANÁLISE",
            font=ctk.CTkFont(weight="bold"),
            command=self._executar_analise,
        )
        self.botao_executar.pack(side="left", fill="x", expand=True)

        # https://open.spotify.com/album/6a5n1Frj3nxGcyTqT1xfrg?si=U3lOYZ1fRB6_7huqJxx1Ug&utm_source=whatsapp
        self.label_status = ctk.CTkLabel(frame, text="Carregando...", justify="left", anchor="w")
        self.label_status.pack(fill="x", padx=10, pady=(0, 10))

    def _montar_bloco_proporcoes(self):
        frame = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        frame.pack(fill="x", padx=12, pady=(0, 12))
        self.frame_proporcoes = frame

        self.fig_pizza = Figure(figsize=(4.4, 3.6), dpi=100)
        self.ax_pizza = self.fig_pizza.add_subplot(111)
        self.canvas_pizza = FigureCanvasTkAgg(self.fig_pizza, master=frame)
        self.canvas_pizza.get_tk_widget().pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        self.fig_estado = Figure(figsize=(4.8, 3.6), dpi=100)
        self.ax_estado = self.fig_estado.add_axes([0.52, 0.08, 0.46, 0.84])
        self.canvas_estado = FigureCanvasTkAgg(self.fig_estado, master=frame)
        self.canvas_estado.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5, pady=10)

        self.fig_classe = Figure(figsize=(4.8, 3.6), dpi=100)
        self.ax_classe = self.fig_classe.add_axes([0.52, 0.08, 0.46, 0.84])
        self.canvas_classe = FigureCanvasTkAgg(self.fig_classe, master=frame)
        self.canvas_classe.get_tk_widget().pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)
        
    def _montar_bloco_tempo_mensal(self):
        self.frame_tempo_mensal = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.frame_tempo_mensal.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.fig_tempo = Figure(figsize=(10, 3), dpi=100)
        self.ax_tempo = self.fig_tempo.add_subplot(111)
        self.canvas_tempo = FigureCanvasTkAgg(self.fig_tempo, master=self.frame_tempo_mensal)
        self.canvas_tempo.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


    def _montar_bloco_bigo(self):
        self.frame_bigo = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.frame_bigo.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        ctk.CTkLabel(
            self.frame_bigo, text="📈 Crescimento Real dos Algoritmos (Big O empírico)",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 4))

        self.label_bigo_status = ctk.CTkLabel(
            self.frame_bigo, text="⏳ Medindo desempenho nesta máquina...",
            font=ctk.CTkFont(size=11), text_color="#888888",
        )
        self.label_bigo_status.pack(anchor="w", padx=10, pady=(0, 6))

        self.fig_bigo = Figure(figsize=(10, 4), dpi=100)
        self.ax_bigo = self.fig_bigo.add_subplot(111)
        self.canvas_bigo = FigureCanvasTkAgg(self.fig_bigo, master=self.frame_bigo)
        self.canvas_bigo.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 6))

        self.texto_bigo = ctk.CTkTextbox(self.frame_bigo, wrap="word", height=140)
        self.texto_bigo.pack(fill="x", padx=10, pady=(0, 10))
        self.texto_bigo.configure(state="disabled")

        self.ax_bigo.set_xlabel("Tamanho da entrada (n)")
        self.ax_bigo.set_ylabel("Tempo (ms) — escala logarítmica")
        self.ax_bigo.set_yscale("log")
        self.ax_bigo.set_title("Crescimento do tempo de execução por tamanho de entrada", fontsize=11, fontweight="bold")
        self.ax_bigo.grid(True, which="both", linestyle="--", alpha=0.4)

        # https://open.spotify.com/intl-pt/album/5S3gls8Kjn8KVmqlIDEBbO?si=1mKFNiy7S-CNKo5x1b__Zg

    def _atualizar_grafico_pizza(self, faixas):
        self.ax_pizza.clear()
        valores = list(faixas.values())
        rotulos = list(faixas.keys())
        cores = ["#66BB6A", "#FFA726", "#EF5350"]

        if sum(valores) == 0:
            self.ax_pizza.text(0.5, 0.5, "Sem dados", ha="center", va="center")
        else:
            self.ax_pizza.pie(valores, labels=rotulos, autopct="%1.1f%%", colors=cores, startangle=90,
                               textprops={"fontsize": 9})
        self.ax_pizza.set_title("Proporção de Áreas de Alerta por Faixa (km²)", fontsize=11, fontweight="bold")
        self.fig_pizza.tight_layout()
        self.canvas_pizza.draw()

    def _ler_datas(self):
        formato = "%d/%m/%Y"
        try:
            data_inicio = dt.datetime.strptime(self.entry_data_inicio.get().strip(), formato).date()
        except ValueError:
            data_inicio = None
        try:
            data_fim = dt.datetime.strptime(self.entry_data_fim.get().strip(), formato).date()
        except ValueError:
            data_fim = None
        return data_inicio, data_fim

    def _carregar_e_executar(self):
        self._rodar_em_segundo_plano(carregar=True)

    def _executar_analise(self):
        self._rodar_em_segundo_plano(carregar=False)

    def _rodar_em_segundo_plano(self, carregar):
        if getattr(self, "_processando", False):
            return
        self._processando = True
        self.botao_executar.configure(text="⏳ PROCESSANDO...")
        self.label_status.configure(text="⏳ Processando, aguarde...\n")

        data_inicio, data_fim = self._ler_datas()

        def trabalho_pesado():
            erro = None
            saida = None
            try:
                if carregar:
                    self.motor.carregar_base_ativa()
                saida = self.motor.executar_analise(data_inicio, data_fim)
            except EcoSortDataError as e:
                erro = e
            self.after(0, lambda: self._finalizar_analise(saida, erro))

        threading.Thread(target=trabalho_pesado, daemon=True).start()

    def _finalizar_analise(self, saida, erro):
        self._processando = False
        self.botao_executar.configure(text="EXECUTAR ANÁLISE")

        if erro is not None:
            messagebox.showwarning("Aviso", str(erro))
            self.label_status.configure(text="⚠️ Não foi possível concluir a análise.")
            return

        self.label_status.configure(
            text=(
                f"⏱️ Tempo TOTAL do processo (carregar dados + calcular tudo): {saida['tempo_total']:.3f}s\n"
                f"📊 Amostra usada no benchmark: {self.motor.tamanho_amostra} / {len(self.motor.dados_area)} registros"
            )
        )

        self._atualizar_grafico_pizza(saida["faixas"])
        texto_relatorio_completo = (
            saida["relatorio"] + "\n\n" + saida["diagnostico_texto"]
            + "\n\n" + self.texto_corretude
        )
        self._atualizar_relatorio(texto_relatorio_completo)
        self._atualizar_diagnostico(saida["melhor"], saida["melhor_aleatorio"])
        self._atualizar_resumo_oficial(saida)
        self._atualizar_grafico_estado(saida["estado"])
        self._atualizar_grafico_classe(saida["classe"])
        self._atualizar_grafico_tempo(saida["tempo_mensal"])
        self._atualizar_grafico_comparativo(saida["resultados"])
        self._atualizar_visibilidade_detalhado()

        if not getattr(self, "_bigo_calculado", False):
            self._bigo_calculado = True
            self._calcular_bigo_em_segundo_plano()               


    def _montar_bloco3_relatorio(self):
        frame = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        frame.pack(fill="x", padx=12, pady=(0, 6))
        self.frame_relatorio = frame

        ctk.CTkLabel(
            frame, text="📄 Relatório de Impacto Ambiental",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(8, 4))


        self.texto_relatorio = ctk.CTkTextbox(frame, wrap="word", height=90)
        self.texto_relatorio.pack(fill="x", padx=10, pady=(0, 10))
        self.texto_relatorio.configure(state="disabled")

    def _montar_bloco4_diagnostico(self):
        self.frame_diagnostico = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.frame_diagnostico.pack(fill="x", padx=12, pady=(0, 12))
        self.frame_diagnostico.grid_columnconfigure(0, weight=1)
        self.frame_diagnostico.grid_columnconfigure(1, weight=1)

        painel_melhor = ctk.CTkFrame(self.frame_diagnostico, corner_radius=8, fg_color="#E8F5E9")
        painel_melhor.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        ctk.CTkLabel(
            painel_melhor, text="🏆 MELHOR DESEMPENHO",
            font=ctk.CTkFont(weight="bold"), text_color="#1B5E20",
        ).pack(anchor="w", padx=10, pady=(8, 0))
        ctk.CTkLabel(
            painel_melhor, text="(tempo individual do algoritmo — não é o tempo total)",
            font=ctk.CTkFont(size=10), text_color="#558B2F",
        ).pack(anchor="w", padx=10, pady=(0, 4))
        self.label_melhor = ctk.CTkLabel(painel_melhor, text="—", justify="left", anchor="w")
        self.label_melhor.pack(anchor="w", padx=10, pady=(0, 10), fill="x")
        #
        painel_pior = ctk.CTkFrame(self.frame_diagnostico, corner_radius=8, fg_color="#FFEBEE")
        painel_pior.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        ctk.CTkLabel(
            painel_pior, text="⚠️ PIOR DESEMPENHO",
            font=ctk.CTkFont(weight="bold"), text_color="#B71C1C",
        ).pack(anchor="w", padx=10, pady=(8, 0))
        ctk.CTkLabel(
            painel_pior, text="(tempo individual do algoritmo — não é o tempo total)",
            font=ctk.CTkFont(size=10), text_color="#C62828",
        ).pack(anchor="w", padx=10, pady=(0, 4))
        self.label_pior = ctk.CTkLabel(painel_pior, text="—", justify="left", anchor="w")
        self.label_pior.pack(anchor="w", padx=10, pady=(0, 10), fill="x")

    def _montar_bloco_comparativo(self):
        self.frame_comparativo = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.frame_comparativo.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        ctk.CTkLabel(
            self.frame_comparativo,
            text="📊 Comparação de Tempos Reais por Algoritmo (dados desta planilha)",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 4))

        self.fig_comparativo = Figure(figsize=(10, 4), dpi=100)
        self.ax_comparativo = self.fig_comparativo.add_subplot(111)
        self.canvas_comparativo = FigureCanvasTkAgg(self.fig_comparativo, master=self.frame_comparativo)
        self.canvas_comparativo.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _montar_bloco_resumo_oficial(self):
        self.frame_resumo_oficial = ctk.CTkFrame(self.scroll_frame, corner_radius=10, fg_color="#E3F2FD")

        ctk.CTkLabel(
            self.frame_resumo_oficial, text="📋 Resumo Oficial do Período Filtrado",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#0D47A1",
        ).pack(anchor="w", padx=10, pady=(10, 6))

        grade = ctk.CTkFrame(self.frame_resumo_oficial, fg_color="transparent")
        grade.pack(anchor="w", padx=10, pady=(0, 12), fill="x")
        grade.grid_columnconfigure(0, minsize=30)

        icones = ["🗺️", "📍", "🏞️", "🔥", "📅"]
        self.labels_resumo_valores = []
        for i, icone in enumerate(icones):
            ctk.CTkLabel(grade, text=icone, font=ctk.CTkFont(size=13), anchor="w").grid(
                row=i, column=0, sticky="w", pady=3
            )
            texto = ctk.CTkLabel(grade, text="—", font=ctk.CTkFont(size=12, weight="bold"), anchor="w", justify="left")
            texto.grid(row=i, column=1, sticky="w", pady=3)
            self.labels_resumo_valores.append(texto)


    def _atualizar_grafico_estado(self, estado):
        self.ax_estado.clear()
        valores = list(estado.values())
        nomes = [_formatar_nome_categoria(n) for n in estado.keys()]

        for leg in self.fig_estado.legends:
            leg.remove()

        if sum(valores) == 0:
            self.ax_estado.text(0.5, 0.5, "Sem dados", ha="center", va="center")
        else:
            total = sum(valores)
            cores = ["#1565C0", "#EF6C00", "#2E7D32", "#C62828", "#6A1B9A",
                     "#00838F", "#AD1457", "#9E9D24", "#5D4037", "#455A64"]
            wedges, _ = self.ax_estado.pie(valores, colors=cores[:len(valores)], startangle=90)
            rotulos = [f"{n} — {v:,.0f} km² ({v/total*100:.1f}%)" for n, v in zip(nomes, valores)]
            self.fig_estado.legend(
                wedges, rotulos,
                loc="center left",
                bbox_to_anchor=(0.02, 0.5),
                fontsize=7.5,
                frameon=False,
            )

        self.fig_estado.suptitle("Regiões Afetadas (km²)", fontsize=10, fontweight="bold")
        self.canvas_estado.draw()

    def _atualizar_grafico_classe(self, classe):
        self.ax_classe.clear()
        valores = list(classe.values())
        nomes = [_formatar_nome_categoria(n) for n in classe.keys()]

        for leg in self.fig_classe.legends:
            leg.remove()

        if sum(valores) == 0:
            self.ax_classe.text(0.5, 0.5, "Sem dados", ha="center", va="center")
        else:
            total = sum(valores)
            cores = ["#1565C0", "#EF6C00", "#2E7D32", "#C62828", "#6A1B9A",
                     "#00838F", "#AD1457", "#9E9D24", "#5D4037", "#455A64"]
            wedges, _ = self.ax_classe.pie(valores, colors=cores[:len(valores)], startangle=90)
            rotulos = [f"{n} — {v:,.0f} km² ({v/total*100:.1f}%)" for n, v in zip(nomes, valores)]
            self.fig_classe.legend(
                wedges, rotulos,
                loc="center left",
                bbox_to_anchor=(0.02, 0.5),
                fontsize=7.5,
                frameon=False,
            )

        self.fig_classe.suptitle("Área por Classe de Alerta (km²)", fontsize=10, fontweight="bold")
        self.canvas_classe.draw()

    def _atualizar_grafico_tempo(self, tempo_dict):
        self.ax_tempo.clear()
        if not tempo_dict:
            self.ax_tempo.text(0.5, 0.5, "Sem dados de data", ha="center", va="center")
        else:
            meses = list(tempo_dict.keys())
            valores = list(tempo_dict.values())
            self.ax_tempo.bar(meses, valores, color="#2E7D32")
            self.ax_tempo.set_xticks(range(len(meses)))
            self.ax_tempo.set_xticklabels(meses, rotation=45, ha="right", fontsize=7)
        self.ax_tempo.set_ylabel("Área (km²)")
        self.ax_tempo.set_title("Distribuição de Área ao Longo do Tempo", fontsize=10, fontweight="bold")
        self.fig_tempo.tight_layout()
        self.canvas_tempo.draw()

    def _atualizar_visibilidade_detalhado(self):
        frames_detalhados = [
            self.frame_proporcoes,
            self.frame_tempo_mensal,
            self.frame_relatorio,
            self.frame_bigo,
            self.frame_comparativo,
        ]

        for frame in frames_detalhados:
            frame.pack_forget()
        self.frame_resumo_oficial.pack_forget()

        if self.motor.modo_com_filtro:
            self.frame_resumo_oficial.pack(fill="x", padx=12, pady=(0, 12), before=self.frame_diagnostico)
        else:
            for frame in frames_detalhados:
                frame.pack(fill="both", expand=True, padx=12, pady=(0, 12), before=self.frame_diagnostico)

    def _atualizar_relatorio(self, texto):
        self.texto_relatorio.configure(state="normal")
        self.texto_relatorio.delete("1.0", "end")
        self.texto_relatorio.insert("1.0", texto)
        self.texto_relatorio.configure(state="disabled")

    def _atualizar_diagnostico(self, diag_inverso, diag_aleatorio):
        self.label_melhor.configure(
            text=(
                f"Cenário Invertido (pior caso)\n"
                f"Algoritmo: {diag_inverso['melhor_nome']}\n"
                f"Tempo: {diag_inverso['melhor_tempo']*1000:.4f} ms\n"
                f"Classe: {diag_inverso['melhor_complexidade']}\n\n"
                f"Cenário Aleatório\n"
                f"Algoritmo: {diag_aleatorio['melhor_nome']}\n"
                f"Tempo: {diag_aleatorio['melhor_tempo']*1000:.4f} ms\n"
                f"Classe: {diag_aleatorio['melhor_complexidade']}"
            )
        )
        self.label_pior.configure(
            text=(
                f"Cenário Invertido (pior caso)\n"
                f"Algoritmo: {diag_inverso['pior_nome']}\n"
                f"Tempo: {diag_inverso['pior_tempo']*1000:.4f} ms\n"
                f"Classe: {diag_inverso['pior_complexidade']}\n\n"
                f"Cenário Aleatório\n"
                f"Algoritmo: {diag_aleatorio['pior_nome']}\n"
                f"Tempo: {diag_aleatorio['pior_tempo']*1000:.4f} ms\n"
                f"Classe: {diag_aleatorio['pior_complexidade']}"
            )
        )

    def _calcular_bigo_em_segundo_plano(self):
        def trabalho():
            dados_crescimento = medir_crescimento()
            diagnostico_bigo = gerar_diagnostico_bigo(dados_crescimento)
            self.after(0, lambda: self._atualizar_grafico_bigo(dados_crescimento, diagnostico_bigo))

        threading.Thread(target=trabalho, daemon=True).start()

    def _atualizar_grafico_bigo(self, dados_crescimento, diagnostico_bigo):
        self.label_bigo_status.configure(text="✅ Medição concluída nesta máquina")

        self.ax_bigo.clear()
        cores = {
            "Bubble Sort": "#C62828",
            "Selection Sort": "#EF6C00",
            "Insertion Sort": "#F9A825",
            "Merge Sort": "#2E7D32",
            "Quick Sort": "#1565C0",
        }
        estilos = {
            "Bubble Sort": "-",
            "Selection Sort": "-",
            "Insertion Sort": "-",
            "Merge Sort": "--",
            "Quick Sort": ":",
        }

        for nome, dados in dados_crescimento.items():
            tamanhos = dados["tamanhos"]
            tempos_ms = [t * 1000 for t in dados["tempos"]]
            classe = diagnostico_bigo[nome]["classe"]
            cor = cores.get(nome, "#555555")
            estilo = estilos.get(nome, "-")

            self.ax_bigo.plot(
                tamanhos, tempos_ms, marker="o", linewidth=2, linestyle=estilo, color=cor,
                label=f"{nome} — {classe}",
            )

        self.ax_bigo.set_xlabel("Tamanho da entrada (n)")
        self.ax_bigo.set_ylabel("Tempo (ms) — escala logarítmica")
        self.ax_bigo.set_yscale("log")
        self.ax_bigo.set_title("Crescimento do tempo de execução por tamanho de entrada", fontsize=11, fontweight="bold")
        self.ax_bigo.legend(fontsize=8, loc="upper left")
        self.ax_bigo.grid(True, which="both", linestyle="--", alpha=0.4)
        self.fig_bigo.tight_layout()
        self.canvas_bigo.draw()
        self.update_idletasks()

        texto_final = "\n\n".join(diagnostico_bigo[nome]["texto"] for nome in dados_crescimento)
        self.texto_bigo.configure(state="normal")
        self.texto_bigo.delete("1.0", "end")
        self.texto_bigo.insert("1.0", texto_final)
        self.texto_bigo.configure(state="disabled")
        

    def _atualizar_grafico_comparativo(self, resultados):
        self.ax_comparativo.clear()

        algoritmos = list(resultados["Inverso"].keys())
        tempos_inverso = [resultados["Inverso"][nome] * 1000 for nome in algoritmos]
        tempos_aleatorio = [resultados["Aleatorio"][nome] * 1000 for nome in algoritmos]

        posicoes = range(len(algoritmos))
        largura = 0.35

        barras_inverso = self.ax_comparativo.bar(
            [i - largura / 2 for i in posicoes], tempos_inverso, largura,
            label="Invertido (pior caso)", color="#C62828",
        )
        barras_aleatorio = self.ax_comparativo.bar(
            [i + largura / 2 for i in posicoes], tempos_aleatorio, largura,
            label="Aleatório", color="#1565C0",
        )

        for barra in list(barras_inverso) + list(barras_aleatorio):
            altura = barra.get_height()
            self.ax_comparativo.annotate(
                f"{altura:.2f}",
                (barra.get_x() + barra.get_width() / 2, altura),
                textcoords="offset points", xytext=(0, 3),
                ha="center", fontsize=7,
            )

        self.ax_comparativo.set_xticks(list(posicoes))
        self.ax_comparativo.set_xticklabels(algoritmos, fontsize=9)
        self.ax_comparativo.set_ylabel("Tempo (ms)")
        self.ax_comparativo.set_title(
            f"Tempo de ordenação por algoritmo — amostra de {self.motor.tamanho_amostra} registros reais (areaMunKm)",
            fontsize=10, fontweight="bold",
        )
        self.ax_comparativo.legend(fontsize=8)
        self.ax_comparativo.grid(True, axis="y", linestyle="--", alpha=0.4)
        self.fig_comparativo.tight_layout()
        self.canvas_comparativo.draw()
        self.update_idletasks()

    def _atualizar_resumo_oficial(self, saida):
        total_area = sum(self.motor.dados_area) if self.motor.dados_area else 0
        total_alertas = len(self.motor.dados_area)
        qtd_estados = len(saida["estado"]) if saida["estado"] else 0

        if saida["classe"]:
            classe_predominante = max(saida["classe"], key=saida["classe"].get)
            classe_predominante = _formatar_nome_categoria(classe_predominante)
        else:
            classe_predominante = "—"

        area_fmt = f"{total_area:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        alertas_fmt = f"{total_alertas:,}".replace(",", ".")

        textos = [
            f"Área total analisada: {area_fmt} km²",
            f"Registros de alerta: {alertas_fmt}",
            f"Estados afetados: {qtd_estados}",
            f"Classe predominante: {classe_predominante}",
            f"Período: {self.entry_data_inicio.get()} a {self.entry_data_fim.get()}",
        ]
        for label, texto in zip(self.labels_resumo_valores, textos):
            label.configure(text=texto)

    # https://open.spotify.com/album/2srjzxgFaYLNh8UlJPAJ8b?si=7DEdtlSEQCOSIUJvdE9s7Q&utm_source=whatsapp
    def _alternar_filtro(self):
        if getattr(self, "_processando", False):
            return
        self.motor.modo_com_filtro = not self.motor.modo_com_filtro
        if self.motor.modo_com_filtro:
            self.botao_toggle.configure(
                text="🔄 MODO ATUAL: COM FILTRO (Clique p/ alternar)",
                fg_color=COR_COM_FILTRO,
                hover_color="#E65100",
            )
        else:
            self.botao_toggle.configure(
                text="🔄 MODO ATUAL: SEM FILTRO (Clique p/ alternar)",
                fg_color=COR_SEM_FILTRO,
                hover_color="#1B5E20",
            )
        self._carregar_e_executar()

def iniciar_aplicacao():
    app = InterfaceEcoSort()
    app.mainloop()

if __name__ == "__main__":
    iniciar_aplicacao()
