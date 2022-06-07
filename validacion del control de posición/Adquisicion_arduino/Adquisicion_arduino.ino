/*boolean anterior = 0;    
boolean actual = 0; 
int contador = 0;  

void setup() 
{
  Serial.begin(9600);  
  pinMode(52,INPUT);    
}

 boolean debounce(boolean dato_anterior) 
 {

   boolean dato_actual = digitalRead(52);
   if (dato_anterior != dato_actual)
   {
     delay(10);
     dato_actual = digitalRead(52);
   }
   return dato_actual;
 }  

void loop() 
{           

  actual = debounce(anterior); 
  

  if ( anterior == 0 && actual == 1) 
  {
         contador++;                      
         Serial.println(contador);
  }
  
    anterior = actual;
}*/

void setup() 
{
  Serial.begin(9600);  
  pinMode(52,INPUT);
  pinMode(53,INPUT);    
}

void loop() 
{                             
   Serial.println(digitalRead(52));
   Serial.println(digitalRead(53));
}
