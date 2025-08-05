import io
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import TableStyle


class EnhancedPixReportGenerator:
    """Gerador de relatórios PIX com formatação aprimorada e opções de detalhamento"""

    def __init__(self, report_type="detailed"):
        """
        Inicializa o gerador de relatórios

        Args:
            report_type (str): Tipo do relatório - "summary" ou "detailed"
        """
        self.buffer = io.BytesIO()
        self.pagesize = landscape(A4)
        self.width, self.height = self.pagesize
        self.styles = getSampleStyleSheet()
        self.report_type = report_type

        # Timezone do Brasil (UTC-3)
        self.brazil_timezone = timezone(timedelta(hours=-3))

        # Margens
        self.left_margin = 30
        self.right_margin = 30
        self.top_margin = 120  # Espaço maior para cabeçalho institucional
        self.bottom_margin = 50

        # Cores institucionais
        self.primary_color = colors.Color(0.2, 0.3, 0.6)  # Azul escuro
        self.secondary_color = colors.Color(0.8, 0.8, 0.8)  # Cinza claro
        self.accent_color = colors.Color(0.1, 0.4, 0.7)  # Azul médio

        self.setup_styles()

    def to_brazil_timezone(self, dt):
        """
        Converte uma data/hora para o timezone do Brasil (UTC-3)

        Args:
            dt (datetime): Data/hora a ser convertida

        Returns:
            datetime: Data/hora no timezone do Brasil
        """
        if dt is None:
            return None

        # Se a data não tem timezone, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)

        # Converte para o timezone do Brasil
        return dt.astimezone(self.brazil_timezone)

    def setup_styles(self):
        """Configura os estilos de texto aprimorados para o documento"""

        # Título principal
        self.styles.add(
            ParagraphStyle(
                name="MainTitle",
                fontName="Helvetica-Bold",
                fontSize=16,
                alignment=1,  # Centralizado
                spaceAfter=10,
                textColor=self.primary_color,
            ),
        )

        # Subtítulo
        self.styles.add(
            ParagraphStyle(
                name="Subtitle",
                fontName="Helvetica-Bold",
                fontSize=12,
                alignment=1,
                spaceAfter=8,
                textColor=self.accent_color,
            ),
        )

        # Cabeçalho de seção
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                fontName="Helvetica-Bold",
                fontSize=11,
                alignment=0,
                spaceAfter=6,
                spaceBefore=12,
                textColor=self.primary_color,
                backColor=self.secondary_color,
                borderPadding=8,
            ),
        )

        # Título de chave
        self.styles.add(
            ParagraphStyle(
                name="ChaveTitle",
                fontName="Helvetica-Bold",
                fontSize=10,
                alignment=0,
                spaceAfter=4,
                spaceBefore=8,
                textColor=self.accent_color,
            ),
        )

        # Texto normal melhorado
        self.styles.add(
            ParagraphStyle(
                name="EnhancedNormal",
                fontName="Helvetica",
                fontSize=9,
                alignment=0,
                spaceAfter=2,
                leading=11,
            ),
        )

        # Texto pequeno para dados técnicos
        self.styles.add(
            ParagraphStyle(
                name="SmallText",
                fontName="Helvetica",
                fontSize=8,
                alignment=0,
                spaceAfter=1,
                leading=9,
                textColor=colors.Color(0.4, 0.4, 0.4),
            ),
        )

    def create_header_footer(self, canvas, doc):
        """Cria o cabeçalho e rodapé institucional em cada página"""
        canvas.saveState()

        # CABEÇALHO INSTITUCIONAL
        y_start = self.height

        # Título do relatório
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(colors.black)
        if self.report_type == "detailed":
            report_title = "RELATÓRIO DE CONSULTA PIX - DETALHADO"
        else:
            report_title = "RELATÓRIO DE CONSULTA PIX - RESUMIDO"
        canvas.drawCentredString(self.width / 2, y_start - 80, report_title)

        # Linha decorativa
        canvas.setStrokeColor(self.primary_color)
        canvas.setLineWidth(2)
        canvas.line(40, y_start - 95, self.width - 40, y_start - 95)

        # RODAPÉ
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.black)

        # Data e hora de geração
        now = datetime.now(self.brazil_timezone)
        canvas.drawString(40, 25, f"Gerado em: {now.strftime('%d/%m/%Y às %H:%M:%S')}")

        # Classificação de sigilo
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(colors.red)
        canvas.drawCentredString(self.width / 2, 15, "RESTRITO - USO INTERNO")

        # Numeração de página
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.black)
        canvas.drawRightString(self.width - 40, 25, f"Página {doc.page}")

        canvas.restoreState()

    def create_summary_info(self, requisicao_data):
        """Cria seção de informações resumidas da requisição"""
        story = []

        # Seção de informações da consulta
        story.append(Paragraph("INFORMAÇÕES DA CONSULTA", self.styles["SectionHeader"]))
        story.append(Spacer(1, 6))

        # Tabela com informações da requisição
        data_criacao = requisicao_data.get("criado_em")
        data_criacao_brasil = self.to_brazil_timezone(data_criacao)
        data_formatada = (
            data_criacao_brasil.strftime("%d/%m/%Y às %H:%M:%S")
            if data_criacao_brasil
            else "N/A"
        )

        data = [
            ["Tipo de Consulta:", requisicao_data.get("tipo_requisicao", "N/A")],
            ["Termo Pesquisado:", requisicao_data.get("termo_busca", "N/A")],
            ["Motivo da Consulta:", requisicao_data.get("motivo", "N/A")],
            ["Responsável:", requisicao_data.get("responsavel", "N/A")],
            ["Data da Consulta:", data_formatada],
        ]

        table = Table(data, colWidths=[150, 400])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), self.secondary_color),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ],
            ),
        )

        story.append(table)
        story.append(Spacer(1, 20))

        return story

    def generate_summary_report(self, requisicao_data, chaves_pix):
        """Gera relatório resumido - apenas informações das chaves"""
        story = []

        # Informações da consulta
        story.extend(self.create_summary_info(requisicao_data))

        # Resumo quantitativo
        total_chaves = len(chaves_pix)
        story.append(Paragraph("RESUMO QUANTITATIVO", self.styles["SectionHeader"]))
        story.append(Spacer(1, 6))

        summary_data = [
            ["Total de Chaves Encontradas:", str(total_chaves)],
            [
                "Chaves Ativas:",
                str(
                    sum(
                        1
                        for chave in chaves_pix
                        if chave.get("status", "").upper() == "ATIVO"
                    ),
                ),
            ],
            [
                "Chaves Inativas:",
                str(
                    sum(
                        1
                        for chave in chaves_pix
                        if chave.get("status", "").upper() != "ATIVO"
                    ),
                ),
            ],
        ]

        summary_table = Table(summary_data, colWidths=[200, 100])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), self.secondary_color),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ],
            ),
        )

        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Lista de chaves (resumida)
        if chaves_pix:
            story.append(
                Paragraph("CHAVES PIX ENCONTRADAS", self.styles["SectionHeader"]),
            )
            story.append(Spacer(1, 10))

            # Cabeçalho da tabela
            headers = [
                "Chave PIX",
                "Status",
                "CPF/CNPJ",
                "Nome do Proprietário",
                "Instituição Financeira",
                "Data Criação",
            ]

            # Dados das chaves
            table_data = [headers]

            for chave in chaves_pix:
                data_abertura = chave.get("data_abertura_conta")
                data_abertura_brasil = self.to_brazil_timezone(data_abertura)
                data_abertura_formatada = (
                    data_abertura_brasil.strftime("%d/%m/%Y")
                    if data_abertura_brasil
                    else "N/A"
                )

                row = [
                    Paragraph(str(chave.get("chave", "N/A")), self.styles["SmallText"]),
                    Paragraph(
                        str(chave.get("status", "N/A")),
                        self.styles["SmallText"],
                    ),
                    Paragraph(
                        str(chave.get("cpf_cnpj", "N/A")),
                        self.styles["SmallText"],
                    ),
                    Paragraph(
                        str(chave.get("nome_proprietario", "N/A")),
                        self.styles["SmallText"],
                    ),
                    Paragraph(str(chave.get("banco", "N/A")), self.styles["SmallText"]),
                    Paragraph(data_abertura_formatada, self.styles["SmallText"]),
                ]
                table_data.append(row)

            # Configurar larguras das colunas
            total_width = self.width - self.left_margin - self.right_margin
            col_widths = [
                total_width * 0.25,  # Chave
                total_width * 0.10,  # Status
                total_width * 0.15,  # CPF/CNPJ
                total_width * 0.25,  # Nome
                total_width * 0.15,  # Banco
                total_width * 0.10,  # Data
            ]

            table = Table(table_data, colWidths=col_widths)
            table.setStyle(
                TableStyle(
                    [
                        # Cabeçalho
                        ("BACKGROUND", (0, 0), (-1, 0), self.primary_color),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                        # Dados
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        # Bordas e linhas
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("LINEBELOW", (0, 0), (-1, 0), 1, self.primary_color),
                        # Padding
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        # Zebra stripes
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.Color(0.96, 0.96, 0.96)],
                        ),
                    ],
                ),
            )

            story.append(table)

        return story

    def generate_detailed_report(self, requisicao_data, chaves_pix):
        """Gera relatório detalhado - informações das chaves e eventos"""
        story = []

        # Informações da consulta
        story.extend(self.create_summary_info(requisicao_data))

        # Chaves PIX detalhadas
        if chaves_pix:
            story.append(
                Paragraph("DETALHAMENTO DAS CHAVES PIX", self.styles["SectionHeader"]),
            )
            story.append(Spacer(1, 10))

            for i, chave in enumerate(chaves_pix):
                # Título da chave
                chave_num = i + 1
                chave_valor = chave.get('chave', 'N/A')
                chave_status = chave.get('status', 'N/A')
                chave_title = (
                    f"CHAVE {chave_num}: {chave_valor} - Status: {chave_status}"
                )
                story.append(Paragraph(chave_title, self.styles["ChaveTitle"]))
                story.append(Spacer(1, 6))

                # Informações básicas da chave
                data_abertura_chave = chave.get("data_abertura_conta")
                data_abertura_chave_brasil = self.to_brazil_timezone(
                    data_abertura_chave,
                )
                data_abertura_formatada = (
                    data_abertura_chave_brasil.strftime("%d/%m/%Y")
                    if data_abertura_chave_brasil
                    else "N/A"
                )

                chave_info = [
                    ["Tipo de Chave:", chave.get("tipo_chave", "N/A")],
                    ["CPF/CNPJ do Proprietário:", chave.get("cpf_cnpj", "N/A")],
                    ["Nome do Proprietário:", chave.get("nome_proprietario", "N/A")],
                    ["Instituição Financeira:", chave.get("banco", "N/A")],
                    ["Agência:", chave.get("agencia", "N/A")],
                    ["Número da Conta:", chave.get("numero_conta", "N/A")],
                    ["Tipo da Conta:", chave.get("tipo_conta", "N/A")],
                    ["Data de Abertura da Conta:", data_abertura_formatada],
                ]

                info_table = Table(chave_info, colWidths=[150, 400])
                info_table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, 0),
                                (0, -1),
                                colors.Color(0.9, 0.9, 0.9),
                            ),
                            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ],
                    ),
                )

                story.append(info_table)
                story.append(Spacer(1, 12))

                # Eventos relacionados
                eventos = chave.get("eventos_vinculo", [])
                if eventos:
                    story.append(
                        Paragraph(
                            "Histórico de Eventos:",
                            self.styles["EnhancedNormal"],
                        ),
                    )
                    story.append(Spacer(1, 6))

                    # Cabeçalho da tabela de eventos
                    eventos_headers = [
                        "Data/Hora",
                        "Tipo de Evento",
                        "Motivo",
                        "CPF/CNPJ",
                        "Nome",
                        "Instituição",
                        "Abertura Conta",
                    ]

                    eventos_data = [eventos_headers]

                    for evento in eventos:
                        banco_info = f"{evento.get('banco', 'N/A')}"
                        if evento.get("agencia"):
                            banco_info += f"\nAg: {evento.get('agencia')}"
                        if evento.get("numero_conta"):
                            banco_info += f"\nConta: {evento.get('numero_conta')}"

                        data_evento = evento.get("data_evento")
                        data_evento_brasil = self.to_brazil_timezone(data_evento)
                        data_evento_formatada = (
                            data_evento_brasil.strftime("%d/%m/%Y %H:%M")
                            if data_evento_brasil
                            else "N/A"
                        )

                        data_abertura_evento = evento.get("data_abertura_conta")
                        data_abertura_evento_brasil = self.to_brazil_timezone(
                            data_abertura_evento,
                        )
                        if data_abertura_evento_brasil:
                            data_abertura_evento_formatada = (
                                data_abertura_evento_brasil.strftime("%d/%m/%Y")
                            )
                        else:
                            data_abertura_evento_formatada = "N/A"

                        row = [
                            Paragraph(data_evento_formatada, self.styles["SmallText"]),
                            Paragraph(
                                str(evento.get("tipo_evento", "N/A")),
                                self.styles["SmallText"],
                            ),
                            Paragraph(
                                str(evento.get("motivo_evento", "N/A")),
                                self.styles["SmallText"],
                            ),
                            Paragraph(
                                str(evento.get("cpf_cnpj", "N/A")),
                                self.styles["SmallText"],
                            ),
                            Paragraph(
                                str(evento.get("nome_proprietario", "N/A")),
                                self.styles["SmallText"],
                            ),
                            Paragraph(banco_info, self.styles["SmallText"]),
                            Paragraph(
                                data_abertura_evento_formatada,
                                self.styles["SmallText"],
                            ),
                        ]
                        eventos_data.append(row)

                    # Larguras das colunas para eventos
                    total_width = self.width - self.left_margin - self.right_margin
                    eventos_col_widths = [
                        total_width * 0.12,  # Data
                        total_width * 0.15,  # Evento
                        total_width * 0.15,  # Motivo
                        total_width * 0.12,  # CPF/CNPJ
                        total_width * 0.18,  # Nome
                        total_width * 0.18,  # Banco
                        total_width * 0.10,  # Data Conta
                    ]

                    eventos_table = Table(eventos_data, colWidths=eventos_col_widths)
                    eventos_table.setStyle(
                        TableStyle(
                            [
                                # Cabeçalho
                                ("BACKGROUND", (0, 0), (-1, 0), self.accent_color),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, 0), 8),
                                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                                # Dados
                                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                                ("FONTSIZE", (0, 1), (-1, -1), 7),
                                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                # Bordas
                                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                                ("LINEBELOW", (0, 0), (-1, 0), 1, self.accent_color),
                                # Padding
                                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                                ("TOPPADDING", (0, 0), (-1, -1), 6),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                                # Zebra stripes
                                (
                                    "ROWBACKGROUNDS",
                                    (0, 1),
                                    (-1, -1),
                                    [colors.white, colors.Color(0.95, 0.95, 0.95)],
                                ),
                            ],
                        ),
                    )

                    story.append(eventos_table)

                # Separador entre chaves
                if i < len(chaves_pix) - 1:
                    story.append(Spacer(1, 20))
                    story.append(PageBreak())

        return story

    def generate_report(self, requisicao_data, chaves_pix):
        """Gera o relatório completo baseado no tipo selecionado"""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
        )

        if self.report_type == "summary":
            story = self.generate_summary_report(requisicao_data, chaves_pix)
        else:
            story = self.generate_detailed_report(requisicao_data, chaves_pix)

        # Adicionar observações finais
        story.append(Spacer(1, 20))
        story.append(Paragraph("OBSERVAÇÕES IMPORTANTES", self.styles["SectionHeader"]))
        story.append(Spacer(1, 6))

        observacoes = [
            "• Este relatório contém informações sigilosas obtidas através de consulta ao Sistema PIX "  # noqa: E501
            "do Banco Central do Brasil.",
            "• O uso inadequado das informações contidas neste documento pode constituir crime "  # noqa: E501
            "previsto na Lei de Lavagem de Dinheiro.",
            "• Este documento deve ser manuseado apenas por pessoas autorizadas e com necessidade "  # noqa: E501
            "de conhecer as informações.",
            "• A reprodução ou divulgação não autorizada deste relatório é vedada.",
        ]

        for obs in observacoes:
            story.append(Paragraph(obs, self.styles["SmallText"]))
            story.append(Spacer(1, 4))

        # Construir o documento
        doc.build(
            story,
            onFirstPage=self.create_header_footer,
            onLaterPages=self.create_header_footer,
        )

        self.buffer.seek(0)
        return self.buffer
