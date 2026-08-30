import bpy
import math
import os
from mathutils import Vector, Matrix


ROOT = r"C:\Users\rnals\portfolio-prototype"
OUT = os.path.join(ROOT, "assets", "projects", "blender")
os.makedirs(OUT, exist_ok=True)


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1.0,)


def material(name, color, metallic=0.0, roughness=0.38, emission=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = 2.5
    return mat


BLUE = material("PF_Blue", rgb("#5276E6"), 0.12, 0.28)
BLUE_DARK = material("PF_BlueDark", rgb("#24449B"), 0.2, 0.3)
CYAN = material("PF_Cyan", rgb("#43C7C1"), 0.08, 0.25)
ORANGE = material("PF_CutSurface", rgb("#FF7A45"), 0.05, 0.3)
YELLOW = material("PF_Yellow", rgb("#FFC857"), 0.05, 0.3)
RED = material("PF_Control", rgb("#FF4F68"), 0.1, 0.24, rgb("#A91E42"))
PURPLE = material("PF_Purple", rgb("#815AC0"), 0.1, 0.3)
INK = material("PF_Ink", rgb("#202637"), 0.0, 0.5)
LIGHT = material("PF_Light", rgb("#EEF2FF"), 0.0, 0.55)
WHITE = material("PF_White", rgb("#FFFFFF"), 0.0, 0.45)


def activate_scene(scene):
    bpy.context.window.scene = scene
    bpy.context.view_layer.update()


def new_scene(name):
    old = bpy.data.scenes.get(name)
    if old:
        bpy.data.scenes.remove(old)
    scene = bpy.data.scenes.new(name)
    activate_scene(scene)
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.world = bpy.data.worlds.new(name + "_World")
    scene.world.color = rgb("#F4F6FB")[:3]
    scene.view_settings.look = "AgX - Medium High Contrast"
    return scene


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def add_cube(scene, name, loc, scale, mat, bevel=0.15):
    activate_scene(scene)
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Portfolio Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 4
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return assign(obj, mat)


def add_uv_sphere(scene, name, loc, scale, mat, segments=48):
    activate_scene(scene)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=24, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    return assign(obj, mat)


def add_cylinder_between(scene, name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    d = b - a
    if d.length < 1e-5:
        return None
    activate_scene(scene)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=d.length,
                                        location=(a + b) * 0.5)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    bpy.ops.object.shade_smooth()
    return assign(obj, mat)


def add_torus(scene, name, loc, major, minor, mat, rotation=(0, 0, 0)):
    activate_scene(scene)
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                    major_segments=48, minor_segments=10,
                                    location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    return assign(obj, mat)


def add_text(scene, body, loc, size=0.42, mat=INK, align="CENTER", extrude=0.012):
    activate_scene(scene)
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, 0))
    obj = bpy.context.object
    obj.data.body = body
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = extrude
    obj.data.bevel_depth = 0.003
    assign(obj, mat)
    return obj


def add_floor(scene, z=-2.15, size=18):
    return add_cube(scene, "Stage", (0, 0, z), (size, size, 0.08), WHITE, 0.06)


def camera_and_lights(scene, camera_loc, target, lens=52):
    activate_scene(scene)
    bpy.ops.object.camera_add(location=camera_loc)
    cam = bpy.context.object
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    for name, loc, energy, size, color in (
        ("Key", (-7, -8, 11), 1500, 6.0, (1.0, 0.86, 0.75)),
        ("Fill", (8, -3, 7), 1100, 5.0, (0.7, 0.82, 1.0)),
        ("Rim", (2, 7, 9), 1300, 4.0, (0.78, 0.88, 1.0)),
    ):
        bpy.ops.object.light_add(type="AREA", location=loc)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        light.rotation_euler = (Vector(target) - light.location).to_track_quat("-Z", "Y").to_euler()


def render(scene, filename):
    activate_scene(scene)
    scene.render.filepath = os.path.join(OUT, filename)
    bpy.ops.render.render(write_still=True)


def selected_only(obj):
    bpy.ops.object.mode_set(mode="OBJECT") if bpy.context.object and bpy.context.object.mode != "OBJECT" else None
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def center_world(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return sum(pts, Vector()) / max(len(pts), 1)


def scene_meshcut_plane():
    scene = new_scene("01_MeshCutter_PlaneCut")
    add_floor(scene)
    source = add_uv_sphere(scene, "CutTarget", (0, 0, 0), (3.0, 3.0, 2.15), BLUE)
    source.data.materials.append(ORANGE)
    scene.mc_cap_material = ORANGE
    selected_only(source)
    op = bpy.ops.meshcut.cut_plane(axis="Z", offset=0.0, keep="BOTH", fill=True,
                                   separate=True, triangulate_cap=False, dist=0.0001)
    pieces = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    for obj in pieces:
        c = center_world(obj)
        obj.location.z += 0.52 if c.z >= 0 else -0.52
        obj.rotation_euler.y += math.radians(-5 if c.z >= 0 else 5)
    add_torus(scene, "CutGuide", (0, 0, 0), 3.05, 0.035, ORANGE)
    add_text(scene, "PLANE CUT", (0, 1.2, 4.05), 0.52, INK)
    add_text(scene, "BOTH SIDES  /  AUTO CAP", (0, 1.2, 3.45), 0.22, PURPLE)
    camera_and_lights(scene, (10.8, -16.5, 8.9), (0, 0, 0.7), 50)
    render(scene, "meshcutter-plane-cut.png")
    return str(op), len(pieces)


def scene_meshcut_fracture():
    scene = new_scene("02_MeshCutter_Fracture")
    add_floor(scene)
    source = add_cube(scene, "FractureTarget", (0, 0, 0), (2.5, 2.5, 2.5), CYAN, 0.35)
    source.data.materials.append(ORANGE)
    scene.mc_cap_material = ORANGE
    scene.cursor.location = (0.35, -0.55, 0.25)
    selected_only(source)
    op = bpy.ops.meshcut.fracture(count=13, mode="IMPACT", rand_seed=7, falloff=3.6,
                                  triangulate=False, set_origin=True, keep_original=False)
    pieces = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    palette = [CYAN, BLUE, PURPLE, YELLOW]
    for i, obj in enumerate(pieces):
        c = center_world(obj)
        v = c - Vector((0, 0, 0))
        if v.length > 1e-5:
            obj.location += v.normalized() * (0.28 + 0.10 * (i % 3))
        obj.rotation_euler.rotate_axis("Z", math.radians((i % 5 - 2) * 2.2))
        if obj.data.materials:
            obj.data.materials[0] = palette[i % len(palette)]
    add_uv_sphere(scene, "ImpactPoint", (0.35, -2.62, 0.25), (0.15, 0.15, 0.15), RED, 24)
    add_text(scene, "IMPACT FRACTURE", (0, 1.3, 4.4), 0.48, INK)
    add_text(scene, "VORONOI  /  13 PIECES", (0, 1.3, 3.85), 0.22, PURPLE)
    camera_and_lights(scene, (11.2, -17.0, 9.7), (0, 0, 0.8), 50)
    render(scene, "meshcutter-impact-fracture.png")
    return str(op), len(pieces)


def create_humanoid_armature(scene, name):
    activate_scene(scene)
    arm_data = bpy.data.armatures.new(name + "Data")
    arm = bpy.data.objects.new(name, arm_data)
    scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    def bone(n, head, tail, parent=None):
        b = eb.new(n)
        b.head, b.tail = head, tail
        if parent:
            b.parent = eb[parent]
        return b

    bone("hips", (0, 0, 3.0), (0, 0, 3.55))
    bone("spine_01", (0, 0, 3.55), (0, 0, 4.25), "hips")
    bone("spine_02", (0, 0, 4.25), (0, 0, 4.9), "spine_01")
    bone("neck", (0, 0, 4.9), (0, 0, 5.25), "spine_02")
    bone("head", (0, 0, 5.25), (0, 0, 6.0), "neck")
    bone("upper_arm.L", (-0.22, 0, 4.75), (-1.35, 0, 4.55), "spine_02")
    bone("forearm.L", (-1.35, 0, 4.55), (-2.25, 0, 4.2), "upper_arm.L")
    bone("hand.L", (-2.25, 0, 4.2), (-2.75, -0.03, 4.05), "forearm.L")
    bone("upper_arm.R", (0.22, 0, 4.75), (1.35, 0, 4.55), "spine_02")
    bone("forearm.R", (1.35, 0, 4.55), (2.25, 0, 4.2), "upper_arm.R")
    bone("hand.R", (2.25, 0, 4.2), (2.75, -0.03, 4.05), "forearm.R")
    bone("thigh.L", (-0.38, 0, 3.1), (-0.52, 0, 1.7), "hips")
    bone("shin.L", (-0.52, 0, 1.7), (-0.48, 0, 0.45), "thigh.L")
    bone("foot.L", (-0.48, 0, 0.45), (-0.48, -0.85, 0.22), "shin.L")
    bone("thigh.R", (0.38, 0, 3.1), (0.52, 0, 1.7), "hips")
    bone("shin.R", (0.52, 0, 1.7), (0.48, 0, 0.45), "thigh.R")
    bone("foot.R", (0.48, 0, 0.45), (0.48, -0.85, 0.22), "shin.R")
    bpy.ops.object.mode_set(mode="OBJECT")
    selected_only(arm)
    return arm


def move_control(arm, key, target):
    pb = arm.pose.bones.get("CTRL_" + key)
    if pb:
        m = pb.matrix.copy()
        m.translation = Vector(target)
        pb.matrix = m
        bpy.context.view_layer.update()


BODY_BONES = (
    "hips", "spine_01", "spine_02", "neck",
    "upper_arm.L", "forearm.L", "hand.L", "upper_arm.R", "forearm.R", "hand.R",
    "thigh.L", "shin.L", "foot.L", "thigh.R", "shin.R", "foot.R",
)


def build_mannequin(scene, arm, prefix, offset=(0, 0, 0), scale=1.0, body_mat=BLUE, controls=True):
    off = Vector(offset)
    created = []
    for name in BODY_BONES:
        pb = arm.pose.bones.get(name)
        if not pb:
            continue
        a = (arm.matrix_world @ pb.head) * scale + off
        b = (arm.matrix_world @ pb.tail) * scale + off
        radius = (0.20 if "spine" in name or name == "hips" else 0.145) * scale
        created.append(add_cylinder_between(scene, prefix + name, a, b, radius, body_mat))
        add_uv_sphere(scene, prefix + name + "Joint", a, (radius * 1.15,) * 3, body_mat, 24)
    head_pb = arm.pose.bones.get("head")
    if head_pb:
        c = ((arm.matrix_world @ head_pb.head) + (arm.matrix_world @ head_pb.tail)) * 0.5
        c = c * scale + off
        add_uv_sphere(scene, prefix + "Head", c, (0.46 * scale, 0.42 * scale, 0.52 * scale), LIGHT, 32)
    if controls:
        for key in ("head", "hand_l", "hand_r", "foot_l", "foot_r"):
            pb = arm.pose.bones.get("CTRL_" + key)
            if pb:
                p = (arm.matrix_world @ pb.head) * scale + off
                add_torus(scene, prefix + "CTRL_" + key, p, 0.25 * scale, 0.045 * scale, RED,
                          rotation=(math.radians(90), 0, 0))
    return created


def prepare_autopose(scene, name="AutoPoseRig"):
    arm = create_humanoid_armature(scene, name)
    selected_only(arm)
    detect = bpy.ops.autopose.detect_bones()
    setup = bpy.ops.autopose.setup_controls()
    bpy.ops.object.mode_set(mode="POSE")
    return arm, str(detect), str(setup)


def apply_dynamic_pose(arm):
    move_control(arm, "hips", (0.15, 0.0, 3.15))
    move_control(arm, "head", (0.05, -0.15, 5.95))
    move_control(arm, "hand_l", (-2.35, -0.35, 5.55))
    move_control(arm, "hand_r", (2.1, -0.5, 3.35))
    move_control(arm, "foot_l", (-0.9, -0.45, 0.42))
    move_control(arm, "foot_r", (0.95, 0.12, 0.62))
    return str(bpy.ops.autopose.pose())


def scene_autopose_controls():
    scene = new_scene("03_AutoPose_ControlRig")
    add_floor(scene, z=-0.1)
    arm, detect, setup = prepare_autopose(scene)
    pose = apply_dynamic_pose(arm)
    build_mannequin(scene, arm, "Pose_", body_mat=BLUE, controls=True)
    arm.hide_render = True
    add_text(scene, "CONTROL-DRIVEN POSE", (0, 0.7, 7.15), 0.46, INK)
    add_text(scene, "DETECT  >  SETUP  >  SOLVE", (0, 0.7, 6.62), 0.21, PURPLE)
    camera_and_lights(scene, (9.2, -16.5, 7.8), (0, 0, 3.1), 58)
    render(scene, "autopose-control-solve.png")
    return detect, setup, pose


def scene_autopose_mirror():
    scene = new_scene("04_AutoPose_Mirror")
    add_floor(scene, z=-0.1, size=22)
    arm, detect, setup = prepare_autopose(scene, "MirrorRig")
    pose = apply_dynamic_pose(arm)
    build_mannequin(scene, arm, "Before_", offset=(-4.0, 0, 0), scale=0.82,
                    body_mat=BLUE, controls=False)
    selected_only(arm)
    bpy.ops.object.mode_set(mode="POSE")
    mirror = str(bpy.ops.autopose.mirror_pose())
    build_mannequin(scene, arm, "After_", offset=(4.0, 0, 0), scale=0.82,
                    body_mat=PURPLE, controls=False)
    arm.hide_render = True
    add_cube(scene, "Divider", (0, 0.8, 3.2), (0.025, 0.04, 3.1), YELLOW, 0.02)
    add_text(scene, "ORIGINAL", (-4.0, 0.7, 6.7), 0.27, BLUE_DARK)
    add_text(scene, "MIRRORED", (4.0, 0.7, 6.7), 0.27, PURPLE)
    add_text(scene, "ONE-CLICK MIRROR POSE", (0, 0.7, 7.45), 0.45, INK)
    camera_and_lights(scene, (0, -22.5, 6.6), (0, 0, 3.2), 55)
    render(scene, "autopose-mirror-pose.png")
    return detect, setup, pose, mirror


MIXAMO_SOURCE = r"C:\Users\rnals\Desktop\Blender\CurrentScene_With_Mixamo.blend"


def world_bounds(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        return Vector((-1, -1, 0)), Vector((1, 1, 2))
    mn = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    mx = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return mn, mx


def append_mixamo(scene, tag, target_height=5.2):
    activate_scene(scene)
    with bpy.data.libraries.load(MIXAMO_SOURCE, link=False) as (_src, dst):
        dst.collections = ["Mixamo_Character"]
    collection = dst.collections[0]
    scene.collection.children.link(collection)
    objects = list(collection.all_objects)
    arm = next(obj for obj in objects if obj.type == "ARMATURE")
    meshes = [obj for obj in objects if obj.type == "MESH"]
    root = next(obj for obj in objects if obj.parent is None)

    arm.animation_data_clear()
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    for obj in meshes:
        for poly in obj.data.polygons:
            poly.use_smooth = True

    bpy.context.view_layer.update()
    mn, mx = world_bounds(meshes)
    factor = target_height / max(mx.z - mn.z, 0.001)
    root.scale *= factor
    bpy.context.view_layer.update()
    mn, mx = world_bounds(meshes)
    center = (mn + mx) * 0.5
    root.location += Vector((-center.x, -center.y, -mn.z))
    bpy.context.view_layer.update()

    root.name = tag + "_Root"
    arm.name = tag + "_Armature"
    arm.hide_render = True
    for i, obj in enumerate(meshes):
        obj.name = f"{tag}_Mesh_{i + 1}"
    return arm, meshes, root


def move_control_world_delta(arm, key, delta):
    pb = arm.pose.bones.get("CTRL_" + key)
    if pb is None:
        return
    current_world = arm.matrix_world @ pb.matrix.translation
    local_target = arm.matrix_world.inverted() @ (current_world + Vector(delta))
    matrix = pb.matrix.copy()
    matrix.translation = local_target
    pb.matrix = matrix
    bpy.context.view_layer.update()


def prepare_mixamo_autopose(scene, tag):
    arm, meshes, root = append_mixamo(scene, tag)
    selected_only(arm)
    detect = str(bpy.ops.autopose.detect_bones())
    setup = str(bpy.ops.autopose.setup_controls())
    bpy.ops.object.mode_set(mode="POSE")
    mn, mx = world_bounds(meshes)
    return arm, meshes, root, mx.z - mn.z, detect, setup


def apply_mixamo_pose(arm, height):
    move_control_world_delta(arm, "hips", (0.03 * height, 0, 0.02 * height))
    move_control_world_delta(arm, "head", (0, -0.04 * height, 0.04 * height))
    move_control_world_delta(arm, "hand_l", (-0.12 * height, -0.08 * height, 0.30 * height))
    move_control_world_delta(arm, "hand_r", (0.06 * height, -0.12 * height, -0.20 * height))
    move_control_world_delta(arm, "foot_l", (-0.10 * height, -0.05 * height, 0.02 * height))
    move_control_world_delta(arm, "foot_r", (0.12 * height, 0.08 * height, 0.13 * height))
    selected_only(arm)
    bpy.ops.object.mode_set(mode="POSE")
    return str(bpy.ops.autopose.pose())


def add_mixamo_control_rings(scene, arm, prefix):
    for key in ("head", "hand_l", "hand_r", "foot_l", "foot_r"):
        pb = arm.pose.bones.get("CTRL_" + key)
        if pb:
            p = arm.matrix_world @ pb.head
            add_torus(scene, prefix + key, p, 0.22, 0.035, RED,
                      rotation=(math.radians(90), 0, 0))


def scene_autopose_controls_mixamo():
    scene = new_scene("03_AutoPose_Mixamo_ControlRig")
    add_floor(scene, z=-0.1, size=15)
    arm, meshes, _root, height, detect, setup = prepare_mixamo_autopose(scene, "MixamoPose")
    pose = apply_mixamo_pose(arm, height)
    add_mixamo_control_rings(scene, arm, "Mixamo_CTRL_")
    mn, mx = world_bounds(meshes)
    top = mx.z
    add_text(scene, "MIXAMO AUTOPOSE", (0, 1.0, top + 0.85), 0.45, INK)
    add_text(scene, "DETECT  >  SETUP  >  ONNX + IK", (0, 1.0, top + 0.34), 0.20, PURPLE)
    camera_and_lights(scene, (9.2, -18.5, 8.1), (0, 0, height * 0.58), 50)
    render(scene, "autopose-mixamo-control-solve.png")
    return detect, setup, pose


def scene_autopose_mirror_mixamo():
    scene = new_scene("04_AutoPose_Mixamo_Mirror")
    add_floor(scene, z=-0.1, size=22)
    left_arm, left_meshes, left_root, height, detect_l, setup_l = prepare_mixamo_autopose(scene, "MixamoOriginal")
    left_root.location.x -= 3.35
    bpy.context.view_layer.update()
    pose_l = apply_mixamo_pose(left_arm, height)
    right_arm, right_meshes, right_root, height_r, detect_r, setup_r = prepare_mixamo_autopose(scene, "MixamoMirrored")
    right_root.location.x += 3.35
    bpy.context.view_layer.update()
    pose_r = apply_mixamo_pose(right_arm, height_r)
    selected_only(right_arm)
    bpy.ops.object.mode_set(mode="POSE")
    mirror = str(bpy.ops.autopose.mirror_pose())
    top = max(world_bounds(left_meshes)[1].z, world_bounds(right_meshes)[1].z)
    add_cube(scene, "MixamoDivider", (0, 0.9, height * 0.5), (0.025, 0.04, height * 0.52), YELLOW, 0.02)
    add_text(scene, "ORIGINAL", (-3.35, 1.0, top + 0.38), 0.24, BLUE_DARK)
    add_text(scene, "MIRRORED", (3.35, 1.0, top + 0.38), 0.24, PURPLE)
    add_text(scene, "MIXAMO MIRROR POSE", (0, 1.0, top + 0.92), 0.43, INK)
    camera_and_lights(scene, (0, -24.0, 7.4), (0, 0, height * 0.58), 50)
    render(scene, "autopose-mixamo-mirror-pose.png")
    return detect_l, setup_l, pose_l, detect_r, setup_r, pose_r, mirror


results = {
    "meshcut_plane": scene_meshcut_plane(),
    "meshcut_fracture": scene_meshcut_fracture(),
    "autopose_controls": scene_autopose_controls_mixamo(),
    "autopose_mirror": scene_autopose_mirror_mixamo(),
}

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "portfolio-blender-scenes.blend"))
result = {"output_dir": OUT, "scenes": list(results.keys()), "operators": results}
