import pymunk


class Body(pymunk.Body):
    def __init__(self, obj=None, *args, **kwargs):
        """Subclass of pymunk.Body that allows the body to have a connection back to the entity using this body."""
        super(Body, self).__init__(*args, **kwargs)
        self.obj = obj

    def __getattr__(self, item):
        return self.obj.__getattribute__(item)
