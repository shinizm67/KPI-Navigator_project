<?php

//phpinfo();
/*
print $_SERVER['SERVER_NAME'] . "<br>";

print $_GET['a'] . "<br>";
print $_GET['b'] . "<br>";
print $_GET['c'] . "<br>";
print $_GET['d'] . "<br>";
print $_GET['e'] . "<br>";
print $_GET['f'] . "<br>";
print $_GET['g'] . "<br>";
print $_GET['h'] . "<br>";
print $_GET['i'] . "<br>";
print $_GET['j'] . "<br>";

print $_POST['AA'] . "<br>";
print $_POST['BB'] . "<br>";
*/
$AA = $_POST['AA'];
$BB = $_POST['BB'];



// if AA and/or BB is set, then connect to the database

// AA BB の条件に応じてDBから値を引っ張ってくる


print <<< __EOL
<html>
<body>
<form method="post" action="test.php">
  <input type="text" name="AA" border="0" size="5" value="$AA"><br>
  <input type="text" name="BB" border="0" size="10" value="$BB"><br>
  <input type="submit" value="送信" onMouseOver=document.getElementById('msg').innerHTML='送信ボタンにマウスオーバーしました'; onMouseOut=document.getElementById('msg').innerHTML='マウスオーバーを外しました';>
</form>

__EOL;

if ($AA) {
    print $AA . "<br>\n";
} else  {
    print "AA is not set.<br>\n";
};

if ($BB) {
    print $BB . "<br>\n";
} else  {
    print "BB is not set.<br>\n";
};

for ($i = 0; $i < 10; $i++) {
    $j = $i + 1;
    print "<div width=\"50\"px>i = $i</div>";
    print "<div width=50px>j = $j</div><br>\n";
};

print <<< __EOL2
</body>
</html>
__EOL2;
?>