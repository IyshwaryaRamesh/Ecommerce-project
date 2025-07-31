# main/__init__.py
# from .ecom_app import EcomApp

# __all__ = ["EcomApp"]
# main/__init__.py
__all__ = ["EcomApp"]

def __getattr__(name):
    if name == "EcomApp":
        from .ecom_app import EcomApp
        return EcomApp
    raise AttributeError(name)

