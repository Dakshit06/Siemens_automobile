import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// --- SCENE SETUP ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x111111);
document.body.appendChild(renderer.domElement);

// --- LIGHTING ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 7.5);
scene.add(directionalLight);

// --- CONTROLS ---
const controls = new OrbitControls(camera, renderer.domElement);
camera.position.set(6, 4, 8);
controls.update();

// --- GRID HELPER ---
const gridHelper = new THREE.GridHelper(50, 50);
scene.add(gridHelper);

// --- VEHICLE COMPONENTS ---
let vehicle = new THREE.Group();
let wheels = [], motor, batteryPack, batteryCells = [];

function createVehicle() {
    const vehicle = new THREE.Group();

    // Chassis
    const chassisGeometry = new THREE.BoxGeometry(2, 0.6, 4.5);
    const chassisMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x007bff, 
        transparent: true, 
        opacity: 0.8,
        metalness: 0.8,
        roughness: 0.2
    });
    const chassis = new THREE.Mesh(chassisGeometry, chassisMaterial);
    chassis.position.y = 0.4;
    vehicle.add(chassis);
    chassis.name = "chassis";

    // Cabin
    const cabinGeometry = new THREE.BoxGeometry(1.8, 0.7, 2.5);
    const cabinMaterial = new THREE.MeshStandardMaterial({ 
        color: 0xcccccc,
        metalness: 0.9,
        roughness: 0.1
    });
    const cabin = new THREE.Mesh(cabinGeometry, cabinMaterial);
    cabin.position.set(0, 1.05, -0.2);
    vehicle.add(cabin);
    cabin.name = "cabin";

    // Wheels
    const wheelGeometry = new THREE.CylinderGeometry(0.35, 0.35, 0.3, 32);
    const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.1, roughness: 0.8 });
    
    const wheels = [];
    const wheelPositions = [
        { x: -1.1, y: 0.35, z: 1.5 }, // Front-left
        { x: 1.1, y: 0.35, z: 1.5 },  // Front-right
        { x: -1.1, y: 0.35, z: -1.5 },// Rear-left
        { x: 1.1, y: 0.35, z: -1.5 }  // Rear-right
    ];

    wheelPositions.forEach((pos, i) => {
        const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(pos.x, pos.y, pos.z);
        vehicle.add(wheel);
        wheels.push(wheel);
        wheel.name = `wheel_${i}`;
    });

    // Motor (simple representation)
    const motorGeometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const motorMaterial = new THREE.MeshStandardMaterial({ color: 0xff4500 });
    const motor = new THREE.Mesh(motorGeometry, motorMaterial);
    motor.position.set(0, 0.3, -1.8);
    vehicle.add(motor);
    motor.name = "motor";

    // Battery Pack (simple representation)
    const batteryGeometry = new THREE.BoxGeometry(1.5, 0.2, 2.5);
    const batteryMaterial = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
    const battery = new THREE.Mesh(batteryGeometry, batteryMaterial);
    battery.position.set(0, 0.1, 0);
    vehicle.add(battery);
    battery.name = "battery";


    return { vehicle, wheels };
}

function init() {
    const { vehicle, wheels } = createVehicle();
    scene.add(vehicle);
    window.vehicle = vehicle;
    window.wheels = wheels;

    // Ground Grid
    const gridHelper = new THREE.GridHelper(50, 50);
    scene.add(gridHelper);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
    directionalLight.position.set(5, 10, 7.5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Camera
    camera.position.set(5, 4, 8);
    camera.lookAt(scene.position);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = false;
    controls.minDistance = 5;
    controls.maxDistance = 50;
    controls.maxPolarAngle = Math.PI / 2;


    // Socket.IO connection
    const socket = io.connect(`http://${document.domain}:${location.port}`);

    socket.on('connect', () => {
        console.log('Connected to WebSocket server!');
    });

    socket.on('telemetry_update', (data) => {
        console.log('Received telemetry:', data);
        updateVehicle(data);
    });

    window.addEventListener('resize', onWindowResize, false);
}

function updateVehicle(data) {
    if (!window.vehicle || !window.wheels) return;

    const speedKmh = data.speed_kmh || 0;
    const wheelRotationSpeed = speedKmh / (2 * Math.PI * 0.35) / 3.6; // rad/s

    // Rotate wheels
    window.wheels.forEach(wheel => {
        wheel.rotation.x += wheelRotationSpeed * 0.1; // 0.1 is a time delta factor
    });

    // Update component colors based on data
    const chassis = window.vehicle.getObjectByName('chassis');
    const motor = window.vehicle.getObjectByName('motor');
    const battery = window.vehicle.getObjectByName('battery');

    if (motor) {
        const motorTemp = data.motor_temp_c || 20;
        const motorColor = new THREE.Color().setHSL(0, 1, THREE.MathUtils.lerp(0.5, 0, (motorTemp - 20) / 80));
        motor.material.color.set(motorColor);
    }

    if (battery) {
        const soc = data.battery_soc || 1;
        const batteryColor = new THREE.Color().setHSL(0.3, 1, THREE.MathUtils.lerp(0.1, 0.5, soc));
        battery.material.color.set(batteryColor);
    }

    // Update info panel
    document.getElementById('speed').textContent = (data.speed_kmh || 0).toFixed(1);
    document.getElementById('soc').textContent = ((data.battery_soc || 0) * 100).toFixed(1);
    document.getElementById('motor-temp').textContent = (data.motor_temp_c || 0).toFixed(1);
}


function animate() {
    requestAnimationFrame(animate);
    // OrbitControls update
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.update();
    renderer.render(scene, camera);
}

init();
animate();
