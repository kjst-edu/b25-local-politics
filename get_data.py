#%%
import requests
from pathlib import Path
from io import StringIO
import pandas as pd
import typer
import shared

# uv run get_data.py get_data (url) (自治体名の略_西暦) と入力してください

app = typer.Typer()

@app.callback()
def callback():
    """
    A Collection of Useful Functions
    """
@app.command()
def get_data(url, name):
    typer.echo(shared.get_data(url, name)) 
       
if __name__ == "__main__":
    app()
#%%