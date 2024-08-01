using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using TMPro;
using UnityEngine;

public class ListPy : MonoBehaviour
{
    private TcpListener tcpListener;
    private Thread listenerThread;
    private bool isRunning;

    public GameObject neck;
    public GameObject target;
    float rotx = 0;

    float posx, posy = 0;

    void Start()
    {
        StartListening("127.0.0.1", 5000);
    }

    void StartListening(string ipAddress, int port)
    {
        isRunning = true;
        listenerThread = new Thread(() => ListenForClients(ipAddress, port));
        listenerThread.Start();
    }

    private void Update()
    {
        if (isRunning)
        {
            Quaternion targetRotation = Quaternion.Euler(-90, 180-rotx, 90);
            neck.transform.rotation = targetRotation;

            target.transform.position = new Vector3(posx, 0, posy);
        }
    }

    private void ListenForClients(string ipAddress, int port)
    {
        try
        {
            tcpListener = new TcpListener(IPAddress.Parse(ipAddress), port);
            tcpListener.Start();
            Debug.Log("Server is listening...");

            while (isRunning)
            {
                TcpClient client = tcpListener.AcceptTcpClient();
                Debug.Log("Client connected!");
                Thread clientThread = new Thread(HandleClientComm);
                clientThread.Start(client);
            }
        }
        catch (Exception e)
        {
            Debug.LogError("Error: " + e.Message);
        }
    }

    private void HandleClientComm(object client_obj)
    {
        TcpClient tcpClient = (TcpClient)client_obj;
        NetworkStream clientStream = tcpClient.GetStream();

        byte[] message = new byte[4096];
        int bytesRead;

        while (isRunning)
        {
            bytesRead = 0;

            try
            {
                bytesRead = clientStream.Read(message, 0, 4096);
            }
            catch
            {
                break;
            }

            if (bytesRead == 0)
            {
                break;
            }

            string receivedData = Encoding.ASCII.GetString(message, 0, bytesRead);
            string[] stringArray = receivedData.Split(',');

            Debug.Log("Received data: " + receivedData);

            rotx = float.Parse(stringArray[0]);

            posx = float.Parse(stringArray[2]);
            posy = float.Parse(stringArray[3]);

        }

        tcpClient.Close();
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        tcpListener.Stop();
        if (listenerThread != null)
        {
            listenerThread.Abort();
        }
    }
}
