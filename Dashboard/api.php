<?php
// On active l'affichage des erreurs pour débugger
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

header('Content-Type: application/json; charset=utf-8');

$host = '127.0.0.1';
$db   = 'cyber_path';
$user = 'admin'; 
$pass = 'admin'; 

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        // Force les types numériques (évite que 0.8 devienne "0.8")
        PDO::ATTR_EMULATE_PREPARES => false, 
        PDO::ATTR_STRINGIFY_FETCHES => false
    ]);

    // On récupère les alertes (Le SELECT * inclut mitigations et data_sources)
    $sql = "SELECT * FROM active_alerts ORDER BY timestamp DESC LIMIT 50";
    $stmt = $pdo->query($sql);
    $alerts = $stmt->fetchAll();

    // On envoie le JSON avec une option de sécurité pour les caractères spéciaux
    echo json_encode($alerts, JSON_UNESCAPED_UNICODE | JSON_PARTIAL_OUTPUT_ON_ERROR);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => 'Database Connection Failure',
        'detail' => $e->getMessage()
    ]);
}
?>