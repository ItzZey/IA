from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Dividend AI Watcher"
    compliance_notice: str = (
        "Cette application fournit une analyse educative et probabiliste. "
        "Elle ne constitue pas un conseil financier personnalise. "
        "Les performances passees ne prejugent pas des performances futures."
    )


settings = Settings()
