----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    18:09:31 05/24/2022 
-- Design Name: 
-- Module Name:    LCD - Behavioral 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
--
-- Dependencies: 
--
-- Revision: 
-- Revision 0.01 - File Created
-- Additional Comments: 
--
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use IEEE.NUMERIC_STD.ALL;


-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity LCD is
	 Generic (clk_div: INTEGER :=50000);
    Port ( clk : in  STD_LOGIC;
           rst : in  STD_LOGIC;
           RS : out  STD_LOGIC;
           RW : out  STD_LOGIC;
           SF_CE0 : out  STD_LOGIC;
           DB : out  STD_LOGIC_VECTOR (3 downto 0);
			  rot_a, rot_b : STD_LOGIC;
			  PWMX, PWMY : out STD_LOGIC;
			  setear : in STD_LOGIC;
			  done : out std_logic;
			  E: BUFFER BIT);
			  
end LCD;

architecture Behavioral of LCD is

	type edos is (init1A, init1B, init2A, init2B, init3A, init3B, borra1, borra2, ctrl1, ctrl2, modo1, modo2, 
						LX0, WX0, XS0, WXX0, XSS0, X10, X20, X30, XP0, XD10, XD20, XB0, XM0, XMM0, XF0, XFF0,
						LX, WX, XS, WXX, XSS, X1, X2, X3, XP, XD1, XD2, XB, XM, XMM, XF, XFF, L20, L2, 
						LY0, WY0, YS0, WYY0, YSS0, Y10, Y20, Y30, YP0, YD10, YD20, YB0, YM0, YMM0, YF0, YFF0,
						LY, WY, YS, WYY, YSS, Y1, Y2, Y3, YP, YD1, YD2, YB, YM, YMM, YF, YFF, R1, R2);
	type steps is (S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11,S12,S13,S14);
					
	signal edoA, edoF : edos :=init1A;
	signal mak : steps := S1;
	signal rotary_a_in: std_logic;
	signal rotary_b_in: std_logic;
	signal rotary_q1: std_logic;
	signal rotary_q2: std_logic;
	signal rotary_in: std_logic_vector(1 downto 0);
	signal rotary_event: std_logic;
	signal rotary_left:std_logic;
	signal delay_rotary_q1:std_logic; 
	signal q: STD_LOGIC_VECTOR (19 downto 0);
	signal xy: STD_LOGIC_VECTOR (3 downto 0) := "0000";
	signal cx1, cx2, cx3, cx4, cx5: STD_LOGIC_VECTOR (3 downto 0) :="0000";
	signal cy1, cy2, cy3, cy4, cy5: STD_LOGIC_VECTOR (3 downto 0) :="0000";
	signal seteard, seteo : std_logic;
	signal btn_prev   : std_logic := '0';
	signal counter    : std_logic_vector(19 downto 0) := (others => '0');
	signal mulx1, muly1 : std_logic_vector (16 downto 0);
	signal mulx2, muly2 : std_logic_vector (12 downto 0);
	signal mulx3, muly3 : std_logic_vector (9 downto 0);
	signal mulx4, muly4 : std_logic_vector (6 downto 0);
	signal mulx5, muly5 : std_logic_vector (2 downto 0);
	signal pulsosx, pulsosy : std_logic_vector (16 downto 0):="00000000000000000";
	signal cuentax, cuentay : std_logic_vector (16 downto 0);
	signal activax, activay : std_logic :='0';
	signal qd : std_logic;
begin

rotary_a_in <= rot_a;
rotary_b_in <= rot_b;


SF_CE0<='1';

done<=not activax and not activay;

Divisor : process(clk)
variable cta: integer range 0 to clk_div;
begin
	if (rising_edge(clk)) then
		cta:=cta+1;
		if (cta=clk_div) then
			E<= not E;
			cta:=0;
		end if;
	end if;
end process Divisor;

Maq : process(E)
begin
	if (E'event and E='1') then
		if (rst='1') then
			edoA<=init1A;
		else
			edoA<=edoF;
		end if;
	end if;
end process Maq;

FSM : process(edoA,cx1,cx2,cx3,cx4,cx5,cy1,cy2,cy3,cy4,cy5)
begin
	case edoA is
		when init1A =>
			RS<='0';
			RW<='0';
			DB<="0010";
			edoF<=init1B;
		when init1B =>
			RS<='0';
			RW<='0';
			DB<="1000";
			edoF<=init2A;
		when init2A =>
			RS<='0';
			RW<='0';
			DB<="0010";
			edoF<=init2B;
		when init2B =>
			RS<='0';
			RW<='0';
			DB<="1000";
			edoF<=init3A;
		when init3A =>
			RS<='0';
			RW<='0';
			DB<="0010";
			edoF<=init3B;
		when init3B =>
			RS<='0';
			RW<='0';
			DB<="1000";
			edoF<=borra1;
		when borra1 =>
			RS<='0';
			RW<='0';
			DB<="0000";
			edoF<=borra2;
		when borra2 =>
			RS<='0';
			RW<='0';
			DB<="0001";
			edoF<=ctrl1;
		when ctrl1 =>
			RS<='0';
			RW<='0';
			DB<="0000";
			edoF<=ctrl2;
		when ctrl2 =>
			RS<='0';
			RW<='0';
			DB<="1100";
			edoF<=modo1;
		when modo1 =>
			RS<='0';
			RW<='0';
			DB<="0000";
			edoF<=modo2;
		when modo2 =>
			RS<='0';
			RW<='0';
			DB<="0110";
			edoF<=LX0;------x
		when LX0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=LX;
		when LX =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=WX0;
		when WX0 =>
			RS<='1';
			RW<='0';
			DB<="0111";
			edoF<=WX;
		when WX =>
			RS<='1';
			RW<='0';
			DB<="1000";
			edoF<=XS0;
		when XS0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=XS;
		when XS =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=WXX0;
		when WXX0 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=WXX;
		when WXX =>
			RS<='1';
			RW<='0';
			DB<="1010";
			edoF<=XSS0;
		when XSS0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=XSS;
		when XSS =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=X10;
		when X10 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=X1;
		when X1 =>
			RS<='1';
			RW<='0';
			DB<=cx1;---x1
			edoF<=X20;
		when X20 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=X2;
		when X2 =>
			RS<='1';
			RW<='0';
			DB<=cx2;--x2
			edoF<=X30;
		when X30 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=X3;
		when X3 =>
			RS<='1';
			RW<='0';
			DB<=cx3;--x3
			edoF<=XP0;
		when XP0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=XP;
		when XP =>
			RS<='1';
			RW<='0';
			DB<="1110";
			edoF<=XD10;
		when XD10 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=XD1;
		when XD1 =>
			RS<='1';
			RW<='0';
			DB<=cx4;--x4
			edoF<=XD20;
		when XD20 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=XD2;
		when XD2 =>
			RS<='1';
			RW<='0';
			DB<=cx5;--x5
			edoF<=XB0;
		when XB0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=XB;
		when XB =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=XM0;
		when XM0 =>
			RS<='1';
			RW<='0';
			DB<="0110";
			edoF<=XM;
		when XM =>
			RS<='1';
			RW<='0';
			DB<="1101";
			edoF<=XMM0;
		when XMM0 =>
			RS<='1';
			RW<='0';
			DB<="0110";
			edoF<=XMM;
		when XMM =>
			RS<='1';
			RW<='0';
			DB<="1101";
			edoF<=XF0;
		when XF0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=XF;
		when XF =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=XFF0;
		when XFF0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=XFF;
		when XFF =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=L20;----y
		when L20 =>
			RS<='0';
			RW<='0';
			DB<="1100";
			edoF<=L2;
		when L2 =>
			RS<='0';
			RW<='0';
			DB<="0000";
			edoF<=LY0;
		when LY0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=LY;
		when LY =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=WY0;
		when WY0 =>
			RS<='1';
			RW<='0';
			DB<="0111";
			edoF<=WY;
		when WY =>
			RS<='1';
			RW<='0';
			DB<="1001";
			edoF<=YS0;
		when YS0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=YS;
		when YS =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=WYY0;
		when WYY0 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=WYY;
		when WYY =>
			RS<='1';
			RW<='0';
			DB<="1010";
			edoF<=YSS0;
		when YSS0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=YSS;
		when YSS =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=Y10;
		when Y10 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=Y1;
		when Y1 =>
			RS<='1';
			RW<='0';
			DB<=cy1;---Y1
			edoF<=Y20;
		when Y20 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=Y2;
		when Y2 =>
			RS<='1';
			RW<='0';
			DB<=cy2;--Y2
			edoF<=Y30;
		when Y30 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=Y3;
		when Y3 =>
			RS<='1';
			RW<='0';
			DB<=cy3;--Y3
			edoF<=YP0;
		when YP0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=YP;
		when YP =>
			RS<='1';
			RW<='0';
			DB<="1110";
			edoF<=YD10;
		when YD10 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=YD1;
		when YD1 =>
			RS<='1';
			RW<='0';
			DB<=cy4;--y4
			edoF<=YD20;
		when YD20 =>
			RS<='1';
			RW<='0';
			DB<="0011";
			edoF<=YD2;
		when YD2 =>
			RS<='1';
			RW<='0';
			DB<=cy5;--y5
			edoF<=YB0;
		when YB0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=YB;
		when YB =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=YM0;
		when YM0 =>
			RS<='1';
			RW<='0';
			DB<="0110";
			edoF<=YM;
		when YM =>
			RS<='1';
			RW<='0';
			DB<="1101";
			edoF<=YMM0;
		when YMM0 =>
			RS<='1';
			RW<='0';
			DB<="0110";
			edoF<=YMM;
		when YMM =>
			RS<='1';
			RW<='0';
			DB<="1101";
			edoF<=YF0;
		when YF0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=YF;
		when YF =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=YFF0;
		when YFF0 =>
			RS<='1';
			RW<='0';
			DB<="0010";
			edoF<=YFF;
		when YFF =>
			RS<='1';
			RW<='0';
			DB<="0000";
			edoF<=R1;
		when R1 =>
			RS<='0';
			RW<='0';
			DB<="1000";
			edoF<=R2;
		when R2 =>
			RS<='0';
			RW<='0';
			DB<="0000";
			edoF<=LX0;
	end case;
end process FSM;

-------------------------

divisorq : process(clk)
begin
	if rising_edge(clk) then
		q<=q+1;
	end if;
end process divisorq;

filtro: process(clk)
begin
if rising_edge(clk) then
rotary_in <= rotary_b_in & rotary_a_in;
case rotary_in is
when "00" => rotary_q1 <= '0';
rotary_q2 <= rotary_q2;
when "01" => rotary_q1 <= rotary_q1;
rotary_q2 <= '0';
when "10" => rotary_q1 <= rotary_q1;
rotary_q2 <= '1';
when "11" => rotary_q1 <= '1';
rotary_q2 <= rotary_q2;
when others => rotary_q1 <= rotary_q1;
rotary_q2 <= rotary_q2;
end case;
end if;
end process filtro;

direccion: process(clk)
begin
if clk'event and clk='1' then

delay_rotary_q1 <= rotary_q1;
if rotary_q1='1' and delay_rotary_q1='0' then
rotary_event <= '1';
rotary_left <= rotary_q2;
else
rotary_event <= '0';
rotary_left <= rotary_left;
end if;
end if;
end process direccion;

perilla: process(clk,rotary_event,rotary_left)
begin
if rising_edge(clk) then
	if rotary_event='1' and rotary_left='0' then --left
		xy<=xy-1;
		if xy="0000" then
			xy<="1001";
		end if;
	end if;
	if rotary_event='1' and rotary_left='1' then --right
			xy<=xy+1;
		if xy="1001" then
			xy<="0000";
		end if;
	end if; 
end if;
end process perilla;

antirrebote : process(clk)
begin
if (clk'event and clk='1') then
	if (btn_prev xor setear) = '1' then
		counter <= (others => '0');
		btn_prev <= setear;
	elsif (counter(19) = '0') then
		counter <= counter + 1;
  	else
		seteo <= btn_prev;
	end if;
end if;
end process antirrebote;

puchar : process (clk, mak, seteo, pulsosx, pulsosy)
constant centenas : std_logic_vector (12 downto 0) :="1001110001000";
constant decenas : std_logic_vector (8 downto 0) :="111110100";
constant unidades : std_logic_vector (5 downto 0):="110010";
constant decimales : std_logic_vector (2 downto 0) :="101";
begin
if (clk'event and clk='1') then
if rst='1'then
	mak<=S1;
	cx1<="0000";
	cx2<="0000";
	cx3<="0000";
	cx4<="0000";	
	cx5<="0000";
	cy1<="0000";
	cy2<="0000";
	cy3<="0000";
	cy4<="0000";
	cy5<="0000";
end if;
	case mak is
		when S1 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S2;
			else
				cx1<=xy;
			end if;
		when S2 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S3;
			else
				cx2<=xy;
			end if;
		when S3 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S4;
			else
				cx3<=xy;
			end if;
		when S4 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S5;
			else
				cx4<=xy;
			end if;
		when S5 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S6;
			else
				cx5<=xy;
			end if;
		when S6 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S7;
			else
				cy1<=xy;
			end if;
		when S7 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S8;
			else
				cy2<=xy;
			end if;
		when S8 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S9;
			else
				cy3<=xy;
			end if;
		when S9 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S10;
			else
				cy4<=xy;
			end if;
		when S10 =>
			seteard<=seteo;
			if seteard='0' and seteo='1' then
				mak<=S11;
			else
				cy5<=xy;
			end if;
		when S11 => 
			seteard<=seteo;
			mulx1<=cx1*centenas;
			mulx2<=cx2*decenas;
			mulx3<=cx3*unidades;
			mulx4<=cx4*decimales;
			if cx5="0000" or cx5="0001" then
				mulx5<="000";
			elsif cx5="0010" or cx5="0011" then
				mulx5<="001";
			elsif cx5="0100" or cx5="0101" then
				mulx5<="010";
			elsif cx5="0110" or cx5="0111" then
				mulx5<="011";
			elsif cx5="1000" or cx5="1001" then
				mulx5<="100";
			end if;
			muly1<=cy1*centenas;
			muly2<=cy2*decenas;
			muly3<=cy3*unidades;
			muly4<=cy4*decimales;
			if cx5="0000" or cy5="0001" then
				muly5<="000";
			elsif cy5="0010" or cy5="0011" then
				muly5<="001";
			elsif cy5="0100" or cy5="0101" then
				muly5<="010";
			elsif cy5="0110" or cy5="0111" then
				muly5<="011";
			elsif cy5="1000" or cy5="1001" then
				muly5<="100";
			end if;
			mak<=S12;
		when S12 =>
			pulsosx<=mulx1+mulx2+mulx3+mulx4+mulx5;
			pulsosy<=muly1+muly2+muly3+muly4+muly5;
			mak<=S13;
		when S13 =>
				activax<='1';
				activay<='1';
				cuentax<="00000000000000000";
				cuentay<="00000000000000000";
				cx1<="0000";
				cx2<="0000";
				cx3<="0000";
				cx4<="0000";	
				cx5<="0000";
				cy1<="0000";
				cy2<="0000";
				cy3<="0000";
				cy4<="0000";
				cy5<="0000";
				mak<=S14;	
		when S14 =>
				qd<=q(19);
				if qd='0' and q(19)='1' then
					if cuentax=pulsosx then
						activax<='0';
					else
						cuentax<=cuentax+1;
					end if;	
				   if cuentay=pulsosy then
						activay<='0';
					else
						cuentay<=cuentay+1;
					end if;
				end if;
				
				if activax='1' then
					PWMX<=q(19);
				else
					PWMX<='0';
				end if;
				
				if activay ='1' then
					PWMY<=q(19);	
				else
					PWMY<='0';
				end if;
				
				if activax='0' and activay='0' then
					mak<=S1;
				end if;
	end case;
end if;
end process puchar;

end Behavioral;

