"""
Script de génération du rapport quotidien
À exécuter via cron à 20h00
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from data.fetcher import DataFetcher
from analysis.metrics import generate_performance_summary
from config.settings import DEFAULT_ASSETS, REPORTS_DIR
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_daily_report(ticker: str = "ENGI.PA", asset_name: str = "ENGIE"):
    """
    Génère le rapport quotidien pour un actif
    
    Args:
        ticker: Symbole Yahoo Finance
        asset_name: Nom de l'actif
    """
    logger.info(f"Starting daily report generation for {asset_name}")
    
    try:
        # Récupérer les données du jour
        fetcher = DataFetcher(ticker, period="1d", interval="5m")
        df = fetcher.get_historical_data()
        
        if df is None or df.empty:
            logger.error(f"No data available for {asset_name}")
            print(f"ERROR: No data available for {asset_name}")
            return
        
        # Calculer les statistiques
        open_price = df['Open'].iloc[0]
        close_price = df['Close'].iloc[-1]
        high = df['High'].max()
        low = df['Low'].min()
        volume = df['Volume'].sum()
        
        # Variation du jour
        price_change = close_price - open_price
        price_change_pct = (price_change / open_price) * 100
        
        # Volatilité intraday
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * 100
        
        # Obtenir les métriques
        metrics = generate_performance_summary(df['Close'])
        
        # Générer le rapport
        report_lines = [
            "=" * 70,
            f"DAILY REPORT - {asset_name} ({ticker})",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            "",
            "DAILY SUMMARY",
            "-" * 70,
            f"Opening Price:       €{open_price:.4f}",
            f"Closing Price:       €{close_price:.4f}",
            f"Highest Price:       €{high:.4f}",
            f"Lowest Price:        €{low:.4f}",
            f"Price Change:        €{price_change:+.4f} ({price_change_pct:+.2f}%)",
            f"Total Volume:        {volume:,.0f}",
            f"Intraday Volatility: {volatility:.4f}%",
            "",
            "PERFORMANCE METRICS",
            "-" * 70,
        ]
        
        # Ajouter les métriques
        for key, value in metrics.items():
            report_lines.append(f"{key:.<35} {value}")
        
        report_lines.extend([
            "",
            "=" * 70,
            ""
        ])
        
        # Afficher dans stdout
        report_text = "\n".join(report_lines)
        print(report_text)
        
        # Sauvegarder dans un fichier
        report_filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        report_path = REPORTS_DIR / report_filename
        
        with open(report_path, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Report saved to {report_path}")
        print(f"\n✅ Report saved to: {report_path}")
        
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        print(f"ERROR: {e}")
        return


def generate_multi_asset_report():
    """Génère un rapport pour plusieurs actifs"""
    print("\n" + "=" * 70)
    print("MULTI-ASSET DAILY REPORT")
    print("=" * 70 + "\n")
    
    for asset_name, ticker in DEFAULT_ASSETS.items():
        print(f"\n{'=' * 70}")
        print(f"{asset_name.upper()}")
        print('=' * 70)
        generate_daily_report(ticker, asset_name)
        print()


if __name__ == "__main__":
    # Si un argument est fourni, l'utiliser comme ticker
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
        asset_name = sys.argv[2] if len(sys.argv) > 2 else ticker
        generate_daily_report(ticker, asset_name)
    else:
        # Sinon, générer pour ENGIE par défaut
        generate_daily_report("ENGI.PA", "ENGIE")
