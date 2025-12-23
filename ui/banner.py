from rich.console import Console
import os
console = Console()

def clear():
    os.system("cls" if os.name == "nt" else "clear")
    console.clear()


def banner():
    """ASCII banner WEB-MON BNPB ala hacking tools."""
    clear()
    ascii_art = r"""

░██╗░░░░░░░██╗███████╗██████╗░  ░░░░░░  ███╗░░░███╗░█████╗░███╗░░██╗
░██║░░██╗░░██║██╔════╝██╔══██╗  ░░░░░░  ████╗░████║██╔══██╗████╗░██║
░╚██╗████╗██╔╝█████╗░░██████╦╝  █████╗  ██╔████╔██║██║░░██║██╔██╗██║
░░████╔═████║░██╔══╝░░██╔══██╗  ╚════╝  ██║╚██╔╝██║██║░░██║██║╚████║
░░╚██╔╝░╚██╔╝░███████╗██████╦╝  ░░░░░░  ██║░╚═╝░██║╚█████╔╝██║░╚███║
░░░╚═╝░░░╚═╝░░╚══════╝╚═════╝░  ░░░░░░  ╚═╝░░░░░╚═╝░╚════╝░╚═╝░░╚══╝

                    Website Monitoring Tool - BNPB
                    Version 2.1 - by @chatgpt plus
"""
    console.print(ascii_art, style="bold green")
    console.print("───────────────────────────────────────────────────────────────────────\n", style="cyan")
