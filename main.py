from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class Database:
    @staticmethod
    def get_connection():
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except Error as e:
            messagebox.showerror("Erreur BDD", f"Connexion impossible :\n{e}")
            return None

    @staticmethod
    def execute_update(query, params=None):
        conn = Database.get_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        except Error as e:
            conn.close()
            messagebox.showerror("Erreur SQL", str(e))
            return None

    @staticmethod
    def execute_select(query, params=None):
        conn = Database.get_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            conn.close()
            return result
        except Error as e:
            conn.close()
            messagebox.showerror("Erreur SQL", str(e))
            return []
#categories
def get_categories():
    return Database.execute_select("SELECT id, nom, description FROM categories ORDER BY nom")

def add_category(nom, description):
    if nom.strip() == "":
        messagebox.showwarning("Erreur", "Le nom est obligatoire.")
        return False
    return Database.execute_update("INSERT INTO categories (nom, description) VALUES (%s, %s)", (nom, description))

def update_category(cat_id, nom, description):
    if nom.strip() == "":
        messagebox.showwarning("Erreur", "Le nom est obligatoire.")
        return False
    return Database.execute_update("UPDATE categories SET nom=%s, description=%s WHERE id=%s", (nom, description, cat_id))

def delete_category(cat_id):
    produits = Database.execute_select("SELECT id FROM produits WHERE categorie_id=%s", (cat_id,))
    if produits:
        messagebox.showwarning("Suppression impossible", f"Cette catégorie est utilisée par {len(produits)} produit(s).")
        return False
    return Database.execute_update("DELETE FROM categories WHERE id=%s", (cat_id,))
#fournisseurs
def get_fournisseurs():
    return Database.execute_select("SELECT id, nom, contact FROM fournisseurs ORDER BY nom")

def add_fournisseur(nom, contact):
    if nom.strip() == "":
        messagebox.showwarning("Erreur", "Le nom est obligatoire.")
        return False
    return Database.execute_update("INSERT INTO fournisseurs (nom, contact) VALUES (%s, %s)", (nom, contact))

def update_fournisseur(four_id, nom, contact):
    if nom.strip() == "":
        messagebox.showwarning("Erreur", "Le nom est obligatoire.")
        return False
    return Database.execute_update("UPDATE fournisseurs SET nom=%s, contact=%s WHERE id=%s", (nom, contact, four_id))

def delete_fournisseur(four_id):
    produits = Database.execute_select("SELECT id FROM produits WHERE fournisseur_id=%s", (four_id,))
    if produits:
        messagebox.showwarning("Suppression impossible", f"Ce fournisseur est référencé par {len(produits)} produit(s).")
        return False
    return Database.execute_update("DELETE FROM fournisseurs WHERE id=%s", (four_id,))
#produits
def get_produits():
    query = """
        SELECT p.id, p.nom, p.prix, p.quantite_stock,
               COALESCE(c.nom, 'Aucune'), COALESCE(f.nom, 'Aucun')
        FROM produits p
        LEFT JOIN categories c ON p.categorie_id = c.id
        LEFT JOIN fournisseurs f ON p.fournisseur_id = f.id
        ORDER BY p.nom
    """
    return Database.execute_select(query)

def add_produit(nom, prix, quantite, categorie_id, fournisseur_id):
    if nom.strip() == "":
        messagebox.showwarning("Erreur", "Nom obligatoire.")
        return False
    try:
        p = float(prix)
        q = int(quantite)
        if p < 0 or q < 0:
            raise ValueError
    except:
        messagebox.showwarning("Valeur invalide", "Prix et quantité positifs.")
        return False
    cat_id = int(categorie_id) if categorie_id and str(categorie_id).strip() else None
    fou_id = int(fournisseur_id) if fournisseur_id and str(fournisseur_id).strip() else None
    return Database.execute_update(
        "INSERT INTO produits (nom, prix, quantite_stock, categorie_id, fournisseur_id) VALUES (%s,%s,%s,%s,%s)",
        (nom, p, q, cat_id, fou_id)
    )

def update_produit(prod_id, nom, prix, quantite, categorie_id, fournisseur_id):
    if nom.strip() == "":
        messagebox.showwarning("Erreur", "Nom obligatoire.")
        return False
    try:
        p = float(prix)
        q = int(quantite)
        if p < 0 or q < 0:
            raise ValueError
    except:
        messagebox.showwarning("Valeur invalide", "Prix et quantité positifs.")
        return False
    cat_id = int(categorie_id) if categorie_id and str(categorie_id).strip() else None
    fou_id = int(fournisseur_id) if fournisseur_id and str(fournisseur_id).strip() else None
    return Database.execute_update(
        "UPDATE produits SET nom=%s, prix=%s, quantite_stock=%s, categorie_id=%s, fournisseur_id=%s WHERE id=%s",
        (nom, p, q, cat_id, fou_id, prod_id)
    )

def delete_produit(prod_id):
    if messagebox.askyesno("Confirmation", "Supprimer ce produit ?"):
        return Database.execute_update("DELETE FROM produits WHERE id=%s", (prod_id,))
    return False

#login
class LoginWindow:
    def __init__(self):
        self.window = Tk()
        self.window.title("Connexion Admin - Gestion de Stock")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.configure(bg="#1b3c5d")
        
        #Label
        style = ttk.Style()
        style.configure("TLabel", background="#2c3e50", foreground="white")
        
        frame = ttk.Frame(self.window, padding=20)
        frame.pack(expand=True)
        
        label_titre = ttk.Label(frame, text="Connexion Administrateur")
        label_titre.grid(row=0, column=0, columnspan=2, pady=10)
        
        label_user = ttk.Label(frame, text="Nom d'utilisateur :")
        label_user.grid(row=1, column=0, sticky='e', pady=5, padx=5)
        self.username = StringVar()
        entry_user = ttk.Entry(frame, textvariable=self.username, width=25)
        entry_user.grid(row=1, column=1, pady=5, padx=5)
        
        label_pass = ttk.Label(frame, text="Mot de passe :")
        label_pass.grid(row=2, column=0, sticky='e', pady=5, padx=5)
        self.password = StringVar()
        entry_pass = ttk.Entry(frame, textvariable=self.password, show="*", width=25)
        entry_pass.grid(row=2, column=1, pady=5, padx=5)
        
        btn_login = ttk.Button(frame, text="Se connecter", command=self.check_login)
        btn_login.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.window.bind('<Return>', lambda e: self.check_login())
        
        self.window.mainloop()
    
    def check_login(self):
        username = self.username.get().strip()
        password = self.password.get()
        if username == "admin" and password == "admin":
            self.window.destroy()
            root = Tk()
            app = StockApp(root)
            root.mainloop()
        else:
            messagebox.showerror("Échec", "Identifiant ou mot de passe incorrect")

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Stock - Administrateur")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.frame_categories = ttk.Frame(self.notebook)
        self.frame_fournisseurs = ttk.Frame(self.notebook)
        self.frame_produits = ttk.Frame(self.notebook)
        
        self.notebook.add(self.frame_categories, text="Catégories")
        self.notebook.add(self.frame_fournisseurs, text="Fournisseurs")
        self.notebook.add(self.frame_produits, text="Produits")
        
        self.init_categories_tab()
        self.init_fournisseurs_tab()
        self.init_produits_tab()
        
        self.status_bar = Label(root, text="Administrateur connecté - accès complet", bd=1, relief=SUNKEN, anchor=W,
                                bg="#2ecc71", fg="white", font=('Segoe UI', 9))
        self.status_bar.pack(side=BOTTOM, fill=X)
        
        self.refresh_categories()
        self.refresh_fournisseurs()
        self.refresh_produits()

    #catégories
    def init_categories_tab(self):
        form_frame = ttk.LabelFrame(self.frame_categories, text="Formulaire catégorie", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        label_nom = ttk.Label(form_frame, text="Nom :")
        label_nom.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.cat_nom = StringVar()
        entry_nom = ttk.Entry(form_frame, textvariable=self.cat_nom, width=30)
        entry_nom.grid(row=0, column=1, padx=5, pady=5)
        
        label_desc = ttk.Label(form_frame, text="Description :")
        label_desc.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.cat_desc = StringVar()
        entry_desc = ttk.Entry(form_frame, textvariable=self.cat_desc, width=50)
        entry_desc.grid(row=1, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        btn_add = ttk.Button(btn_frame, text="Ajouter", command=self.add_category)
        btn_add.pack(side='left', padx=5)
        btn_update = ttk.Button(btn_frame, text="Modifier", command=self.update_category)
        btn_update.pack(side='left', padx=5)
        btn_delete = ttk.Button(btn_frame, text="Supprimer", command=self.delete_category)
        btn_delete.pack(side='left', padx=5)
        
        tree_frame = ttk.Frame(self.frame_categories)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        scroll_x = Scrollbar(tree_frame, orient=HORIZONTAL)
        
        self.tree_categories = ttk.Treeview(tree_frame, columns=('ID', 'Nom', 'Description'), show='headings',
                                            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree_categories.yview)
        scroll_x.config(command=self.tree_categories.xview)
        
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.tree_categories.pack(fill='both', expand=True)
        
        self.tree_categories.heading('ID', text='ID')
        self.tree_categories.heading('Nom', text='Nom')
        self.tree_categories.heading('Description', text='Description')
        self.tree_categories.column('ID', width=50)
        self.tree_categories.column('Nom', width=200)
        self.tree_categories.column('Description', width=400)
        
        self.tree_categories.bind('<<TreeviewSelect>>', self.on_category_select)
    
    def refresh_categories(self):
        for row in self.tree_categories.get_children():
            self.tree_categories.delete(row)
        #remplissage
        for cat in get_categories():
            self.tree_categories.insert('', 'end', values=cat)
    
    def add_category(self):
        if add_category(self.cat_nom.get(), self.cat_desc.get()):
            self.refresh_categories()
            self.cat_nom.set("")
            self.cat_desc.set("")
            messagebox.showinfo("Succès", "Catégorie ajoutée")
    
    def update_category(self):
        selected = self.tree_categories.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Sélectionnez une catégorie")
            return
        cat_id = self.tree_categories.item(selected[0])['values'][0]
        if update_category(cat_id, self.cat_nom.get(), self.cat_desc.get()):
            self.refresh_categories()
            self.cat_nom.set("")
            self.cat_desc.set("")
            messagebox.showinfo("Succès", "Catégorie modifiée")
    
    def delete_category(self):
        selected = self.tree_categories.selection()
        if not selected:
            return
        cat_id = self.tree_categories.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmation", "Supprimer cette catégorie ?"):
            if delete_category(cat_id):
                self.refresh_categories()
                self.cat_nom.set("")
                self.cat_desc.set("")
    
    def on_category_select(self, event):
        selected = self.tree_categories.selection()
        if selected:
            values = self.tree_categories.item(selected[0])['values']
            self.cat_nom.set(values[1])
            self.cat_desc.set(values[2])
    
    #fournisseurs
    def init_fournisseurs_tab(self):
        form_frame = ttk.LabelFrame(self.frame_fournisseurs, text="Formulaire fournisseur", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        label_nom = ttk.Label(form_frame, text="Nom :")
        label_nom.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.four_nom = StringVar()
        entry_nom = ttk.Entry(form_frame, textvariable=self.four_nom, width=30)
        entry_nom.grid(row=0, column=1, padx=5, pady=5)
        
        label_contact = ttk.Label(form_frame, text="Contact :")
        label_contact.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.four_contact = StringVar()
        entry_contact = ttk.Entry(form_frame, textvariable=self.four_contact, width=40)
        entry_contact.grid(row=1, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Ajouter", command=self.add_fournisseur).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Modifier", command=self.update_fournisseur).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Supprimer", command=self.delete_fournisseur).pack(side='left', padx=5)
        
        tree_frame = ttk.Frame(self.frame_fournisseurs)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        scroll_x = Scrollbar(tree_frame, orient=HORIZONTAL)
        
        self.tree_fournisseurs = ttk.Treeview(tree_frame, columns=('ID', 'Nom', 'Contact'), show='headings',
                                              yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree_fournisseurs.yview)
        scroll_x.config(command=self.tree_fournisseurs.xview)
        
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.tree_fournisseurs.pack(fill='both', expand=True)
        
        self.tree_fournisseurs.heading('ID', text='ID')
        self.tree_fournisseurs.heading('Nom', text='Nom')
        self.tree_fournisseurs.heading('Contact', text='Contact')
        
        self.tree_fournisseurs.bind('<<TreeviewSelect>>', self.on_fournisseur_select)
    
    def refresh_fournisseurs(self):
        for row in self.tree_fournisseurs.get_children():
            self.tree_fournisseurs.delete(row)
        for f in get_fournisseurs():
            self.tree_fournisseurs.insert('', 'end', values=f)
    
    def add_fournisseur(self):
        if add_fournisseur(self.four_nom.get(), self.four_contact.get()):
            self.refresh_fournisseurs()
            self.four_nom.set("")
            self.four_contact.set("")
            messagebox.showinfo("Succès", "Fournisseur ajouté")
    
    def update_fournisseur(self):
        selected = self.tree_fournisseurs.selection()
        if not selected:
            return
        fid = self.tree_fournisseurs.item(selected[0])['values'][0]
        if update_fournisseur(fid, self.four_nom.get(), self.four_contact.get()):
            self.refresh_fournisseurs()
            self.four_nom.set("")
            self.four_contact.set("")
            messagebox.showinfo("Succès", "Fournisseur modifié")
    
    def delete_fournisseur(self):
        selected = self.tree_fournisseurs.selection()
        if not selected:
            return
        fid = self.tree_fournisseurs.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmation", "Supprimer ce fournisseur ?"):
            if delete_fournisseur(fid):
                self.refresh_fournisseurs()
                self.four_nom.set("")
                self.four_contact.set("")
    
    def on_fournisseur_select(self, event):
        selected = self.tree_fournisseurs.selection()
        if selected:
            values = self.tree_fournisseurs.item(selected[0])['values']
            self.four_nom.set(values[1])
            self.four_contact.set(values[2])
    
    #produits
    def init_produits_tab(self):
        #recherche
        search_frame = ttk.Frame(self.frame_produits)
        search_frame.pack(fill='x', padx=10, pady=5)
        label_search = ttk.Label(search_frame, text="Rechercher :")
        label_search.pack(side='left', padx=5)
        self.search_var = StringVar()
        self.search_var.trace('w', lambda *a: self.filter_produits())
        entry_search = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        entry_search.pack(side='left', padx=5)
        
        # Formulaire
        form_frame = ttk.LabelFrame(self.frame_produits, text="Formulaire produit", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        label_nom = ttk.Label(form_frame, text="Nom :")
        label_nom.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.prod_nom = StringVar()
        entry_nom = ttk.Entry(form_frame, textvariable=self.prod_nom, width=30)
        entry_nom.grid(row=0, column=1, padx=5, pady=5)
        
        label_prix = ttk.Label(form_frame, text="Prix (DT) :")
        label_prix.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.prod_prix = StringVar()
        entry_prix = ttk.Entry(form_frame, textvariable=self.prod_prix, width=15)
        entry_prix.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        label_qte = ttk.Label(form_frame, text="Quantité :")
        label_qte.grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.prod_qte = StringVar()
        entry_qte = ttk.Entry(form_frame, textvariable=self.prod_qte, width=15)
        entry_qte.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        label_cat = ttk.Label(form_frame, text="Catégorie :")
        label_cat.grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.prod_cat = ttk.Combobox(form_frame, state="readonly", width=27)
        self.prod_cat.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        label_four = ttk.Label(form_frame, text="Fournisseur :")
        label_four.grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.prod_four = ttk.Combobox(form_frame, state="readonly", width=27)
        self.prod_four.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Ajouter", command=self.add_produit).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Modifier", command=self.update_produit).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Supprimer", command=self.delete_produit).pack(side='left', padx=5)
        
        tree_frame = ttk.Frame(self.frame_produits)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        scroll_x = Scrollbar(tree_frame, orient=HORIZONTAL)
        
        self.tree_produits = ttk.Treeview(tree_frame, columns=('ID', 'Nom', 'Prix', 'Stock', 'Catégorie', 'Fournisseur'),
                                          show='headings', yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree_produits.yview)
        scroll_x.config(command=self.tree_produits.xview)
        
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.tree_produits.pack(fill='both', expand=True)
        
        self.tree_produits.heading('ID', text='ID')
        self.tree_produits.heading('Nom', text='Nom')
        self.tree_produits.heading('Prix', text='Prix (DT)')
        self.tree_produits.heading('Stock', text='Stock')
        self.tree_produits.heading('Catégorie', text='Catégorie')
        self.tree_produits.heading('Fournisseur', text='Fournisseur')
        self.tree_produits.column('ID', width=50)
        self.tree_produits.column('Nom', width=200)
        self.tree_produits.column('Prix', width=80)
        self.tree_produits.column('Stock', width=80)
        self.tree_produits.column('Catégorie', width=150)
        self.tree_produits.column('Fournisseur', width=150)
        
        self.tree_produits.bind('<<TreeviewSelect>>', self.on_produit_select)
        
        stats_frame = ttk.LabelFrame(self.frame_produits, text="Statistiques", padding=5)
        stats_frame.pack(fill='x', padx=10, pady=5)
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack()
    
    def refresh_produits(self):
        cats = get_categories()
        fours = get_fournisseurs()
        self.prod_cat['values'] = [f"{c[0]} - {c[1]}" for c in cats] + [""]
        self.prod_four['values'] = [f"{f[0]} - {f[1]}" for f in fours] + [""]
        self.filter_produits()
        self.update_stats()
    
    def filter_produits(self):
        search = self.search_var.get().strip().lower()
        all_prods = get_produits()
        filtered = [p for p in all_prods if search in p[1].lower()] if search else all_prods
        for row in self.tree_produits.get_children():
            self.tree_produits.delete(row)
        for p in filtered:
            self.tree_produits.insert('', 'end', values=p)
    
    def update_stats(self):
        prods = get_produits()
        total_qte = sum(p[3] for p in prods)
        total_val = sum(p[2] * p[3] for p in prods)
        self.stats_label.config(text=f" {len(prods)} produits | Stock total : {total_qte} | Valeur : {total_val:.2f} DT")
        self.status_bar.config(text=f"Administrateur | Produits : {len(prods)} | Stock : {total_qte} | Valeur : {total_val:.2f} DT")
    
    def add_produit(self):
        cat_str = self.prod_cat.get()
        four_str = self.prod_four.get()
        cat_id = cat_str.split(' - ')[0] if cat_str and ' - ' in cat_str else None
        four_id = four_str.split(' - ')[0] if four_str and ' - ' in four_str else None
        if add_produit(self.prod_nom.get(), self.prod_prix.get(), self.prod_qte.get(), cat_id, four_id):
            self.refresh_produits()
            self.clear_produit_form()
            messagebox.showinfo("Succès", "Produit ajouté")
    
    def update_produit(self):
        selected = self.tree_produits.selection()
        if not selected:
            return
        pid = self.tree_produits.item(selected[0])['values'][0]
        cat_str = self.prod_cat.get()
        four_str = self.prod_four.get()
        cat_id = cat_str.split(' - ')[0] if cat_str and ' - ' in cat_str else None
        four_id = four_str.split(' - ')[0] if four_str and ' - ' in four_str else None
        if update_produit(pid, self.prod_nom.get(), self.prod_prix.get(), self.prod_qte.get(), cat_id, four_id):
            self.refresh_produits()
            self.clear_produit_form()
            messagebox.showinfo("Succès", "Produit modifié")
    
    def delete_produit(self):
        selected = self.tree_produits.selection()
        if not selected:
            return
        pid = self.tree_produits.item(selected[0])['values'][0]
        if delete_produit(pid):
            self.refresh_produits()
            self.clear_produit_form()
    
    def on_produit_select(self, event):
        selected = self.tree_produits.selection()
        if selected:
            v = self.tree_produits.item(selected[0])['values']
            self.prod_nom.set(v[1])
            self.prod_prix.set(v[2])
            self.prod_qte.set(v[3])
            cat_nom = v[4]
            four_nom = v[5]
            for item in self.prod_cat['values']:
                if item.endswith(f" - {cat_nom}") or (cat_nom == "Aucune" and item == ""):
                    self.prod_cat.set(item)
                    break
            for item in self.prod_four['values']:
                if item.endswith(f" - {four_nom}") or (four_nom == "Aucun" and item == ""):
                    self.prod_four.set(item)
                    break
    
    def clear_produit_form(self):
        self.prod_nom.set("")
        self.prod_prix.set("")
        self.prod_qte.set("")
        self.prod_cat.set("")
        self.prod_four.set("")

if __name__ == "__main__":
    LoginWindow()