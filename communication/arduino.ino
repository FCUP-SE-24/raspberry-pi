#include <Arduino.h>
#include <SocketIOClient.h>
#include <WiFi.h>

const char* ssid = "WIFI1"; // nome da rede
const char* password = "Senha1"; // password

const char* server_address = "192.168.1.100"; // ip do raspberry (ainda não defenido)
const int server_port = 3000;

SocketIOClient client;

// Resposta aos pedidos do raspberry
void onEvent(const char *payload, size_t length) {
  Serial.println("Evento recebido: " + String(payload));

  if (strcmp(payload, "get_bowl_weight") == 0) {
    // Peso aleatorio
    int weight = random(0, 101);
    client.emit("bowl_weight", String(weight).c_str());
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando ao WiFi...");
  }
  Serial.println("Conectado ao WiFi!");

  client.begin(server_address, server_port);
  client.on("get_bowl_weight", onEvent); 

  while (!client.connected()) {
    client.loop();
  }
}

void loop() {
  // Mantém a conexão Socket.IO
  client.loop();
}
