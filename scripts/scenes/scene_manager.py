from scripts.scenes.sample_scene import SampleScene


class SceneManager:
    def __init__(self, initial_scene=None):
        if initial_scene is None:
            initial_scene = SampleScene()

        self.current_scene = None
        self.go_to(initial_scene)

    def go_to(self, scene):
        self.current_scene = scene
        self.current_scene.scene_manager = self
