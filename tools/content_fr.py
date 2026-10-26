# French (Canadian) versions of the four articles, keyed by slug.
FR = {
'choosing-pos-and-inventory-software-small-business': dict(
 tag="Guide d'achat",
 title="Comment choisir un logiciel de caisse et d'inventaire pour une petite entreprise",
 desc="Une liste pratique pour comparer les systèmes de caisse et d'inventaire : quoi tester, quoi demander et quoi ignorer.",
 short="Choisissez le système qui réussit vos dix tâches essentielles en direct, qui réunit ventes, stocks et comptabilité, qui fonctionne sur un téléphone et dont le prix est prévisible. Ignorez le reste de la démonstration.",
 faq=[("Que doit chercher une petite entreprise dans un logiciel de caisse?", "Cherchez des ventes qui mettent à jour les stocks et la comptabilité automatiquement, un écran qui fonctionne sur un téléphone, l'exportation facile de vos données et un modèle de prix qui n'augmente pas à chaque nouvel utilisateur."),
      ("Comment comparer équitablement les systèmes de caisse et d'inventaire?", "Notez vos dix tâches les plus courantes, demandez à chaque fournisseur de les exécuter en direct avec vos données d'exemple et notez chaque tâche : réussie ou non."),
      ("La caisse et l'inventaire doivent-ils former un seul système?", "Habituellement, oui. Quand un seul système enregistre la vente, la variation de stock et l'écriture comptable, vous évitez les doubles saisies et vos chiffres concordent.")],
 body='''
<p>La plupart des petites entreprises choisissent leur logiciel de caisse et d'inventaire de la même façon : une brève démonstration, un prix mensuel, une intuition. Six mois plus tard, les chiffres de stock sont faux, la comptabilité se fait à la main et personne n'a envie de changer encore. Cette liste vous aide à éviter ce scénario.</p>
<h2>Partez de votre façon de vendre</h2>
<p>Notez les trois ou quatre tâches que votre équipe accomplit chaque jour. Une boulangerie encaisse au comptoir et suit la farine et les boîtes. Un distributeur prend des commandes par téléphone et reçoit des palettes. Un commerce fait les deux. Le logiciel doit s'adapter à ces gestes, et non l'inverse. Si une démonstration passe dix minutes sur des fonctions que vous n'utiliserez jamais, cela vous indique pour qui le produit a été conçu.</p>
<h2>Vérifiez que ventes, stocks et comptabilité forment un seul système</h2>
<p>L'échec le plus courant, ce sont trois outils qui ne se parlent pas. Une vente est saisie à un endroit, le stock est modifié dans un tableur et le comptable reçoit une exportation mensuelle. Posez une question simple pendant la démonstration : <strong>quand je vends un article, qu'est-ce qui change, et où?</strong> Une bonne réponse : le stock diminue, la vente s'inscrit dans les livres et la fiche client est mise à jour, le tout automatiquement.</p>
<h2>Testez-le sur un téléphone</h2>
<p>La réception de marchandises, le comptage des tablettes et la vérification d'un prix se font sur le plancher, pas à un bureau. Ouvrez le produit sur un téléphone et essayez de recevoir une livraison. S'il faut pincer et agrandir l'écran pour appuyer sur un bouton, votre personnel cessera de l'utiliser.</p>
<h2>Demandez ce qu'il advient de vos données</h2>
<ul><li>Pouvez-vous exporter tous vos dossiers, dans un format courant, en tout temps?</li><li>Qui s'occupe des copies de sauvegarde, et à quelle fréquence?</li><li>Combien coûte, en temps et en argent, l'importation de vos clients et produits existants?</li></ul>
<h2>Regardez le modèle de prix, pas seulement le prix</h2>
<p>Un faible prix par utilisateur devient cher quand vous ajoutez des caissiers, des employés d'entrepôt et une tenue de livres. Demandez si les utilisateurs sont illimités, si l'installation est un frais unique et si l'hébergement et les mises à jour sont inclus. Un abonnement mensuel fixe est plus facile à planifier qu'une facture qui change à chaque embauche.</p>
<h2>Vérifiez la langue et la province</h2>
<p>Si vous servez des clients en français et en anglais, vérifiez que les factures, les reçus et les écrans du personnel peuvent changer de langue, et pas seulement le site Web. Vérifiez aussi le traitement des taxes pour votre province.</p>
<h2>Soyez franc sur ce qui est terminé</h2>
<p>Demandez au fournisseur quelles fonctions sont offertes aujourd'hui et lesquelles sont encore en construction. Un fournisseur sérieux vous répondra clairement. Ce qui est étiqueté « bientôt » ne devrait pas entrer dans votre décision d'achat.</p>
<h2>Une méthode de notation simple</h2>
<ol><li>Dressez la liste de vos tâches essentielles, dix au maximum.</li><li>Demandez à chaque fournisseur de les exécuter en direct, avec vos propres données d'exemple.</li><li>Notez chacune : réussie ou non. Ignorez tout le reste.</li></ol>
<p>Le système qui réussit le plus de tâches réelles, avec un modèle de prix prévisible, est habituellement le bon.</p>'''),
'why-inventory-counts-drift': dict(
 tag='Inventaire',
 title="Pourquoi les stocks dérivent, et comment le code-barres règle le problème",
 desc="Les raisons habituelles pour lesquelles vos chiffres de stock ne concordent plus avec la tablette, et les petites habitudes et outils qui comblent l'écart.",
 short="Les stocks dérivent parce que les mouvements et les arrivées ne sont pas enregistrés au moment où ils surviennent. Numériser les codes-barres à la réception, au transfert et à la vente, avec de petits comptages chaque semaine, garde le système et la tablette synchronisés.",
 faq=[("Pourquoi mon inventaire ne correspond-il jamais à la tablette?", "Habituellement parce que les réceptions, transferts, retours ou bris ont été enregistrés en retard, de travers ou pas du tout. Plus l'écart est long entre l'événement et la saisie, plus la dérive est grande."),
      ("La numérisation des codes-barres améliore-t-elle vraiment l'exactitude des stocks?", "Oui. La numérisation identifie l'article exact et l'enregistre au moment où il bouge, ce qui élimine la plupart des fautes de frappe et des oublis."),
      ("À quelle fréquence une petite entreprise doit-elle compter ses stocks?", "Comptez chaque semaine un petit groupe d'articles à forte rotation plutôt que tout l'entrepôt une fois par an. Les problèmes apparaissent plus tôt et sont plus faciles à retracer.")],
 body='''
<p>Vous comptez la tablette le lundi et le système est d'accord. Vendredi, il ne l'est plus. La dérive des stocks est normale, et elle vient presque toujours des mêmes quelques causes.</p>
<h2>Où les chiffres déraillent</h2>
<ul><li><strong>Erreurs de réception.</strong> Une livraison est vérifiée avec le bordereau, mais le bordereau est inexact, ou le décompte est saisi plus tard de mémoire.</li><li><strong>Mouvements non enregistrés.</strong> La marchandise passe d'une pièce, d'un camion ou d'un emplacement à l'autre sans qu'un transfert soit saisi.</li><li><strong>Fautes de frappe.</strong> Un zéro de trop dans une quantité suffit à cacher une pénurie pendant des semaines.</li><li><strong>Retours et bris.</strong> Des articles sont jetés ou retournés aux fournisseurs sans ajustement.</li><li><strong>Substitutions au comptoir.</strong> Un client reçoit une taille différente de celle qui a été encaissée.</li></ul>
<h2>Pourquoi le délai aggrave le problème</h2>
<p>Plus l'écart est long entre un événement et sa saisie, plus il risque d'être oublié ou mal saisi. Les notes sur papier qu'on tape en fin de journée sont la première source de dérive dans les petits entrepôts et commerces.</p>
<h2>Ce que change la numérisation</h2>
<p>La numérisation remplace la saisie au clavier par une caméra ou un lecteur. L'article est identifié par son code : impossible de mal écrire un nom ou de choisir la mauvaise variante. Quand la numérisation se fait au moment de la réception, du transfert ou de la vente, le système est mis à jour pendant que la marchandise est encore entre vos mains.</p>
<h2>Des habitudes qui gardent les chiffres justes</h2>
<ol><li><strong>Recevez en vous fiant au bon de commande,</strong> pas à votre mémoire.</li><li><strong>Enregistrez chaque transfert</strong> entre emplacements, même les courts trajets.</li><li><strong>Comptez un peu chaque semaine.</strong> Les comptages tournants de quelques articles à forte rotation repèrent les problèmes plus vite qu'un gros comptage annuel.</li><li><strong>Examinez les écarts</strong> une fois, puis corrigez la cause, pas seulement le chiffre.</li><li><strong>Donnez au personnel des écrans pour téléphone</strong> pour que la saisie prenne quelques secondes.</li></ol>
<h2>Fixez un seuil de réapprovisionnement pour les articles importants</h2>
<p>Quand les stocks sont exacts, vous pouvez vous fier à une alerte de réapprovisionnement. Un système qui vous indique chaque matin que six articles sont sous leur minimum vous évite de parcourir les tablettes juste pour savoir quoi acheter.</p>
<h2>Commencez petit</h2>
<p>Inutile de tout corriger d'un coup. Choisissez vos vingt articles à plus forte rotation, numérisez leurs entrées et sorties pendant un mois et comparez avec un comptage physique. La plupart des propriétaires voient rapidement la différence.</p>'''),
'bilingual-business-software-canada': dict(
 tag='Canada',
 title="Un logiciel d'affaires bilingue pour les petites entreprises canadiennes",
 desc="Pourquoi le français et l'anglais comptent pour les factures, les reçus et les écrans du personnel, et ce qu'il faut vérifier avant d'acheter.",
 short="Un bon logiciel bilingue permet à chaque utilisateur de choisir sa langue et imprime factures et reçus dans la langue du client, avec la terminologie du français canadien. Testez-le avec vos propres documents avant d'acheter et validez les règles provinciales avec un conseiller.",
 faq=[("Un logiciel d'affaires doit-il être offert en français au Canada?", "Cela dépend de votre province, de vos clients et de votre type d'entreprise. Beaucoup d'entreprises canadiennes servent les deux langues, et un système qui change de langue sans accroc évite de tout ressaisir. Confirmez vos obligations avec un comptable ou un conseiller."),
      ("Que faut-il vérifier dans un logiciel d'affaires bilingue?", "Vérifiez que chaque utilisateur peut choisir sa langue, que les factures et reçus s'impriment dans l'une ou l'autre langue, et que les courriels, rapports et messages d'erreur sont traduits, pas seulement le menu."),
      ("Le français canadien est-il différent du français européen dans un logiciel?", "Oui. Certains termes d'affaires diffèrent, par exemple courriel pour email et téléverser pour upload. Demandez si la traduction a été rédigée pour des utilisateurs canadiens.")],
 body='''
<p>Si vous vendez au Canada, certains de vos clients préféreront le français, et certains de vos employés aussi. Un logiciel qui ne fonctionne bien qu'en anglais crée de la friction des deux côtés du comptoir.</p>
<h2>Où la langue se manifeste</h2>
<ul><li><strong>Documents clients :</strong> factures, soumissions, reçus et relevés.</li><li><strong>Écrans du personnel :</strong> menus, boutons, messages d'erreur et rapports.</li><li><strong>Courriels et notifications</strong> que votre système envoie en votre nom.</li><li><strong>Noms et descriptions de produits</strong> que vous saisissez vous-même.</li></ul>
<h2>Traduire n'est pas parler le français canadien</h2>
<p>Le vocabulaire d'affaires diffère entre la France et le Canada. Les termes pour les reçus, les taxes et les modes de paiement ne sont pas toujours les mêmes, et le personnel remarque quand un écran sonne étranger. Demandez au fournisseur si le français est rédigé pour des utilisateurs canadiens, et faites parcourir une vraie facture par un collègue francophone.</p>
<h2>Questions à poser à un fournisseur</h2>
<ol><li>Chaque utilisateur peut-il choisir sa langue, ou s'agit-il d'un seul réglage pour toute l'entreprise?</li><li>Un client peut-il recevoir des documents en français pendant qu'un autre les reçoit en anglais?</li><li>Les rapports, courriels et messages d'erreur sont-ils traduits, ou seulement le menu principal?</li><li>Qui maintient les traductions quand de nouvelles fonctions sont ajoutées?</li></ol>
<h2>Vérifiez vos propres obligations</h2>
<p>Les exigences linguistiques pour les documents commerciaux et l'affichage varient selon la province et le type d'entreprise. Parlez à votre comptable ou à un conseiller qualifié de ce qui s'applique à vous, plutôt que de vous fier au résumé d'un fournisseur de logiciels.</p>
<h2>L'avantage pratique</h2>
<p>Un système bilingue vous permet d'embaucher dans un bassin plus large, de servir plus de clients et de remettre des documents aux deux parties sans tout ressaisir. Pour une entreprise en croissance qui vend d'une province à l'autre, cela compte de plus en plus chaque année.</p>
<h2>La suite</h2>
<p>Avant d'acheter, demandez une démonstration en français et en anglais avec vos propres noms de produits. Si le système gère les deux sans accroc, vous aurez une préoccupation de moins plus tard.</p>'''),
'cloud-vs-on-premise-for-small-business': dict(
 tag="Guide d'achat",
 title="Logiciel infonuagique ou sur place : lequel convient à une petite entreprise",
 desc="Une comparaison simple des coûts, de l'entretien, des sauvegardes et des risques pour les propriétaires qui décident où héberger leur système.",
 short="Pour la plupart des petites entreprises, un logiciel infonuagique coûte moins cher à exploiter parce que le fournisseur s'occupe de l'hébergement, des mises à jour et des sauvegardes. Le sur place se justifie si vous avez du personnel TI, une connexion Internet peu fiable ou une règle qui exige que les données restent chez vous.",
 faq=[("Un logiciel infonuagique est-il meilleur qu'un logiciel sur place pour une petite entreprise?", "Pour la plupart des petites entreprises, oui. Le fournisseur gère les serveurs, les mises à jour et les sauvegardes, et le personnel peut l'utiliser depuis un téléphone ou n'importe quel emplacement. Le sur place convient aux entreprises qui ont du personnel TI ou qui doivent garder leurs données chez elles."),
      ("Quels sont les coûts cachés d'un logiciel sur place?", "Les serveurs et le matériel de remplacement, le temps consacré aux correctifs et aux sauvegardes, les arrêts de service en cas de panne, et le coût d'ajouter un deuxième emplacement ou du personnel à distance."),
      ("Que demander à un fournisseur de logiciel infonuagique?", "Demandez si vous pouvez exporter toutes vos données, à quelle fréquence les sauvegardes sont faites et où elles sont conservées, si les mises à jour et l'hébergement sont inclus dans les frais, et ce qui se passe si vous perdez Internet quelques heures.")],
 body='''
<p>Les anciens logiciels d'affaires roulaient sur un serveur dans l'arrière-boutique. Les logiciels récents roulent dans le nuage et on y accède par un navigateur ou un téléphone. Pour la plupart des petites entreprises, la différence tient à qui assume l'entretien.</p>
<h2>Ce que veut dire « sur place »</h2>
<p>Vous achetez ou louez un serveur, vous installez le logiciel, vous le tenez à jour et vous en faites les sauvegardes. S'il tombe en panne, quelqu'un de chez vous le répare. Cela peut bien fonctionner pour les entreprises qui ont une personne en TI et une raison de garder les données dans l'immeuble.</p>
<h2>Ce que veut dire « infonuagique »</h2>
<p>Le fournisseur héberge le logiciel, applique les mises à jour et gère les sauvegardes. Vous vous connectez de n'importe où. Vous payez un abonnement au lieu d'acheter de l'équipement au départ.</p>
<h2>Comparez les coûts réels</h2>
<ul><li><strong>Matériel :</strong> serveurs, réseau et remplacement après une panne.</li><li><strong>Temps :</strong> mises à jour, correctifs de sécurité et restauration des sauvegardes.</li><li><strong>Arrêts de service :</strong> qui appeler quand ça cesse de fonctionner un samedi.</li><li><strong>Croissance :</strong> ajouter un deuxième emplacement ou du personnel à distance.</li></ul>
<h2>Où l'infonuagique convient bien</h2>
<p>Le logiciel infonuagique convient aux entreprises dont plusieurs personnes travaillent sur des téléphones et des tablettes, qui ont plus d'un emplacement ou qui n'ont pas de personnel TI dédié. Les mises à jour arrivent sans visite, et tout le monde voit les mêmes chiffres en direct.</p>
<h2>Ce qu'il faut vérifier auprès d'un fournisseur infonuagique</h2>
<ol><li>Pouvez-vous exporter toutes vos données quand vous le voulez?</li><li>À quelle fréquence les sauvegardes sont-elles faites, et où sont-elles conservées?</li><li>Les mises à jour et l'hébergement sont-ils inclus dans les frais mensuels?</li><li>Quel est le plan si vous perdez l'accès à Internet pendant quelques heures?</li></ol>
<h2>Quand le sur place se justifie encore</h2>
<p>Si votre connexion Internet est peu fiable, ou si une règle ou un contrat client exige que les données restent sur place, un système sur place peut être le choix le plus sûr. Soyez honnête : est-ce une vraie exigence ou une habitude?</p>
<h2>Notre point de vue</h2>
<p>Nastaliq est exclusivement infonuagique. L'installation et l'hébergement sont assurés par nous, de sorte qu'une petite équipe consacre son temps à vendre et à recevoir de la marchandise plutôt qu'à entretenir un serveur.</p>'''),
}
