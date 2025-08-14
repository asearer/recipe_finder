const API = "http://localhost:8000";
const tokenDiv = document.getElementById("token");
const errorDiv = document.getElementById("error");
let token = null;

function setToken(t) {
  token = t;
  if (t) {
    tokenDiv.textContent = "Logged in (token set)";
    document.getElementById("logout").style.display = "";
    localStorage.setItem("jwt_token", t);
  } else {
    tokenDiv.textContent = "Not logged in";
    document.getElementById("logout").style.display = "none";
    localStorage.removeItem("jwt_token");
  }
}

document.getElementById("signup").onclick = async () => {
  errorDiv.textContent = "";
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  if (!username || !password) {
    errorDiv.textContent = "Username and password required.";
    return;
  }
  const res = await fetch(API + "/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (res.ok) {
    setToken(data.access_token);
    errorDiv.textContent = "";
  } else {
    errorDiv.textContent = data.detail || JSON.stringify(data);
  }
};

document.getElementById("login").onclick = async () => {
  errorDiv.textContent = "";
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  if (!username || !password) {
    errorDiv.textContent = "Username and password required.";
    return;
  }
  const res = await fetch(API + "/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (res.ok) {
    setToken(data.access_token);
    errorDiv.textContent = "";
  } else {
    errorDiv.textContent = data.detail || JSON.stringify(data);
  }
};

document.getElementById("createRecipe").onclick = async () => {
  errorDiv.textContent = "";
  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value;
  const image_url = document.getElementById("image_url").value;
  const ingredients = document
    .getElementById("ingredients")
    .value.split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (!title) {
    errorDiv.textContent = "Title is required.";
    return;
  }
  if (ingredients.length === 0) {
    errorDiv.textContent = "At least one ingredient required.";
    return;
  }
  const res = await fetch(API + "/recipes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: "Bearer " + token } : {}),
    },
    body: JSON.stringify({ title, description, image_url, ingredients }),
  });
  const data = await res.json();
  if (res.ok) {
    errorDiv.textContent = "";
    await refreshAll();
    document.getElementById("title").value = "";
    document.getElementById("description").value = "";
    document.getElementById("image_url").value = "";
    document.getElementById("ingredients").value = "";
  } else {
    errorDiv.textContent = data.detail || JSON.stringify(data);
  }
};

document.getElementById("doSearch").onclick = async () => {
  errorDiv.textContent = "";
  const q = document.getElementById("q").value;
  const res = await fetch(API + "/search?q=" + encodeURIComponent(q));
  const arr = await res.json();
  const ul = document.getElementById("results");
  ul.innerHTML = "";
  arr.forEach((r) => {
    const li = document.createElement("li");
    li.className = "recipe-item";
    if (r.image_url) {
      const img = document.createElement("img");
      img.src = r.image_url;
      img.alt = r.title;
      img.className = "recipe-img";
      li.appendChild(img);
    }
    const content = document.createElement("div");
    content.className = "recipe-content";
    content.innerHTML =
      "<strong>" +
      r.title +
      "</strong><div>" +
      (r.description || "") +
      "</div><div><em>" +
      r.ingredients.map((i) => i.name).join(", ") +
      "</em></div>";
    li.appendChild(content);
    ul.appendChild(li);
  });
};

async function refreshAll() {
  errorDiv.textContent = "";
  const res = await fetch(API + "/recipes");
  const arr = await res.json();
  const ul = document.getElementById("allrecipes");
  ul.innerHTML = "";
  arr.forEach((r) => {
    const li = document.createElement("li");
    li.className = "recipe-item";
    // Image
    if (r.image_url) {
      const img = document.createElement("img");
      img.src = r.image_url;
      img.alt = r.title;
      img.className = "recipe-img";
      li.appendChild(img);
    }
    // Content
    const content = document.createElement("div");
    content.className = "recipe-content";
    content.innerHTML =
      "<strong>" +
      r.title +
      "</strong><div>" +
      (r.description || "") +
      "</div><div><em>" +
      r.ingredients.map((i) => i.name).join(", ") +
      "</em></div>";
    li.appendChild(content);

    // Actions (edit/delete) if user is owner
    if (token && r.owner_id) {
      const payload = parseJwt(token);
      if (payload && payload.sub) {
        // Only show edit/delete if user is owner
        // We don't have username->id mapping, so allow all users to try edit/delete their own recipes
        // Backend will enforce ownership
        const actions = document.createElement("div");
        actions.className = "recipe-actions";
        const editBtn = document.createElement("button");
        editBtn.textContent = "Edit";
        editBtn.className = "edit-btn";
        editBtn.onclick = () => openEditModal(r);
        actions.appendChild(editBtn);

        const delBtn = document.createElement("button");
        delBtn.textContent = "Delete";
        delBtn.className = "delete-btn";
        delBtn.onclick = () => deleteRecipe(r.id);
        actions.appendChild(delBtn);

        li.appendChild(actions);
      }
    }
    ul.appendChild(li);
  });
}

document.getElementById("refresh").onclick = refreshAll;

// Logout button
document.getElementById("logout").onclick = () => {
  setToken(null);
  errorDiv.textContent = "";
  refreshAll();
};

// Edit modal logic
const editModal = document.getElementById("editModal");
const editForm = document.getElementById("editForm");
const editCancel = document.getElementById("editCancel");

function openEditModal(recipe) {
  document.getElementById("edit_id").value = recipe.id;
  document.getElementById("edit_title").value = recipe.title;
  document.getElementById("edit_image_url").value = recipe.image_url || "";
  document.getElementById("edit_description").value = recipe.description || "";
  document.getElementById("edit_ingredients").value = recipe.ingredients
    .map((i) => i.name)
    .join(", ");
  editModal.style.display = "flex";
}

editCancel.onclick = () => {
  editModal.style.display = "none";
};

editForm.onsubmit = async (e) => {
  e.preventDefault();
  errorDiv.textContent = "";
  const id = document.getElementById("edit_id").value;
  const title = document.getElementById("edit_title").value.trim();
  const image_url = document.getElementById("edit_image_url").value;
  const description = document.getElementById("edit_description").value;
  const ingredients = document
    .getElementById("edit_ingredients")
    .value.split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (!title) {
    errorDiv.textContent = "Title is required.";
    return;
  }
  if (ingredients.length === 0) {
    errorDiv.textContent = "At least one ingredient required.";
    return;
  }
  const res = await fetch(API + "/recipes/" + id, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: "Bearer " + token } : {}),
    },
    body: JSON.stringify({ title, description, image_url, ingredients }),
  });
  const data = await res.json();
  if (res.ok) {
    editModal.style.display = "none";
    errorDiv.textContent = "";
    await refreshAll();
  } else {
    errorDiv.textContent = data.detail || JSON.stringify(data);
  }
};

async function deleteRecipe(id) {
  errorDiv.textContent = "";
  if (!confirm("Are you sure you want to delete this recipe?")) return;
  const res = await fetch(API + "/recipes/" + id, {
    method: "DELETE",
    headers: {
      ...(token ? { Authorization: "Bearer " + token } : {}),
    },
  });
  if (res.ok) {
    await refreshAll();
  } else {
    const data = await res.json();
    errorDiv.textContent = data.detail || JSON.stringify(data);
  }
}

// JWT decode helper
function parseJwt(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join(""),
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

// Persistent login
(function () {
  const stored = localStorage.getItem("jwt_token");
  if (stored) {
    setToken(stored);
  }
  refreshAll();
})();
